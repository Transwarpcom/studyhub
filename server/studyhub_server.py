#!/usr/bin/env python3
"""学习台 StudyHub 内容服务

只依赖 Python 标准库。
  GET  /health
  GET  /manifest            课程树
  GET  /lesson?id=<id>      单节内容
  GET  /replies             答疑回复
  POST /upload              上传题目（图片/PDF/文本）
  GET  /inbox               [admin] 待处理上传列表
  POST /reply               [admin] 追加一条讲解回复

认证：Authorization: Bearer <token>
"""
import json
import os
import re
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

DATA_DIR = os.environ.get("DATA_DIR", "/data")
CONTENT_DIR = os.environ.get("CONTENT_DIR", "/content")
READER_TOKEN = os.environ.get("READER_TOKEN", "gaoshu2026")
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "admin-change-me")
PORT = int(os.environ.get("PORT", "8099"))
MAX_UPLOAD = 25 * 1024 * 1024

INBOX = os.path.join(DATA_DIR, "inbox")
REPLIES = os.path.join(DATA_DIR, "replies.json")
LOCK = threading.Lock()

SAFE_ID = re.compile(r"^[A-Za-z0-9_\-/\.]{1,120}$")


def ensure_dirs():
    os.makedirs(INBOX, exist_ok=True)


def read_json(path, default):
    try:
        with open(path, "rb") as f:
            return json.loads(f.read().decode("utf-8"))
    except Exception:
        return default


def write_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(json.dumps(obj, ensure_ascii=False, indent=2).encode("utf-8"))
    os.replace(tmp, path)


def lesson_path(lid):
    if not SAFE_ID.match(lid or ""):
        return None
    name = lid.replace("/", "_")
    p = os.path.join(CONTENT_DIR, "lessons", name + ".json")
    return p if os.path.isfile(p) else None


def parse_multipart(body, content_type):
    """极简 multipart/form-data 解析，不依赖已移除的 cgi 模块。"""
    m = re.search(r'boundary="?([^";]+)"?', content_type or "")
    if not m:
        return {}
    boundary = ("--" + m.group(1)).encode()
    parts = body.split(boundary)
    out = {}
    for part in parts:
        part = part.strip(b"\r\n")
        if not part or part == b"--":
            continue
        if b"\r\n\r\n" not in part:
            continue
        head, data = part.split(b"\r\n\r\n", 1)
        if data.endswith(b"\r\n"):
            data = data[:-2]
        hs = head.decode("utf-8", "replace")
        nm = re.search(r'name="([^"]*)"', hs)
        fn = re.search(r'filename="([^"]*)"', hs)
        if not nm:
            continue
        key = nm.group(1)
        if fn:
            out[key + "__file"] = (fn.group(1), data, hs)
        else:
            out[key] = data.decode("utf-8", "replace")
    return out


class Handler(BaseHTTPRequestHandler):
    server_version = "StudyHub/1.0"
    protocol_version = "HTTP/1.1"

    def log_message(self, format, *args):
        print("[%s] %s" % (time.strftime("%H:%M:%S"), format % args), flush=True)

    # ---------- 基础 ----------
    def send_body(self, code, body, ctype="application/json; charset=utf-8"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False).encode("utf-8")
        elif isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def token(self):
        h = self.headers.get("Authorization", "")
        return h[7:].strip() if h.startswith("Bearer ") else ""

    def ok_auth(self, admin=False):
        t = self.token()
        if admin:
            return t == ADMIN_TOKEN
        return t in (READER_TOKEN, ADMIN_TOKEN)

    # ---------- GET ----------
    def do_GET(self):
        u = urlparse(self.path)
        path = u.path
        qs = parse_qs(u.query)

        if path in ("/health", "/"):
            return self.send_body(200, {"ok": True, "service": "studyhub", "time": int(time.time())})

        if path == "/manifest":
            if not self.ok_auth():
                return self.send_body(401, {"ok": False, "error": "unauthorized"})
            m = read_json(os.path.join(CONTENT_DIR, "manifest.json"), None)
            if m is None:
                return self.send_body(500, {"ok": False, "error": "manifest missing"})
            return self.send_body(200, m)

        if path == "/lesson":
            if not self.ok_auth():
                return self.send_body(401, {"ok": False, "error": "unauthorized"})
            lid = (qs.get("id") or [""])[0]
            p = lesson_path(lid)
            if not p:
                return self.send_body(404, {"ok": False, "error": "lesson not found", "id": lid})
            return self.send_body(200, read_json(p, {}))

        if path == "/replies":
            if not self.ok_auth():
                return self.send_body(401, {"ok": False, "error": "unauthorized"})
            data = read_json(REPLIES, {"version": 1, "replies": []})
            return self.send_body(200, data)

        if path == "/inbox":
            if not self.ok_auth(admin=True):
                return self.send_body(401, {"ok": False, "error": "unauthorized"})
            items = []
            for fn in sorted(os.listdir(INBOX), reverse=True):
                if fn.endswith(".json"):
                    items.append(read_json(os.path.join(INBOX, fn), {}))
            return self.send_body(200, {"inbox": items[:100]})

        if path.startswith("/inbox/file/"):
            if not self.ok_auth(admin=True):
                return self.send_body(401, {"ok": False, "error": "unauthorized"})
            name = path.split("/")[-1]
            if not re.match(r"^[A-Za-z0-9_\-\.]{1,120}$", name):
                return self.send_body(400, {"ok": False, "error": "bad name"})
            fp = os.path.join(INBOX, name)
            if not os.path.isfile(fp):
                return self.send_body(404, {"ok": False, "error": "not found"})
            with open(fp, "rb") as f:
                data = f.read()
            ctype = "application/octet-stream"
            if name.lower().endswith(".jpg") or name.lower().endswith(".jpeg"):
                ctype = "image/jpeg"
            elif name.lower().endswith(".png"):
                ctype = "image/png"
            elif name.lower().endswith(".pdf"):
                ctype = "application/pdf"
            return self.send_body(200, data, ctype)

        return self.send_body(404, {"ok": False, "error": "no route", "path": path})

    # ---------- POST ----------
    def do_POST(self):
        u = urlparse(self.path)
        path = u.path
        n = int(self.headers.get("Content-Length") or 0)
        if n > MAX_UPLOAD:
            return self.send_body(413, {"ok": False, "error": "too large"})
        body = self.rfile.read(n) if n else b""

        if path == "/upload":
            if not self.ok_auth():
                return self.send_body(401, {"ok": False, "error": "unauthorized"})
            form = parse_multipart(body, self.headers.get("Content-Type", ""))
            fname, fdata, _ = form.get("file__file", ("", b"", ""))
            if not fdata:
                return self.send_body(400, {"ok": False, "error": "no file"})
            uid = time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]
            ext = os.path.splitext(fname)[1].lower()
            if ext not in (".jpg", ".jpeg", ".png", ".heic", ".pdf", ".txt", ".md"):
                ext = ".bin"
            stored = uid + ext
            with open(os.path.join(INBOX, stored), "wb") as f:
                f.write(fdata)
            meta = {
                "id": uid,
                "file": stored,
                "original": fname,
                "bytes": len(fdata),
                "note": form.get("note", ""),
                "created": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "pending",
            }
            write_json(os.path.join(INBOX, uid + ".json"), meta)
            print("[upload] %s %s %d bytes note=%r" % (stored, fname, len(fdata), meta["note"]), flush=True)
            return self.send_body(200, {"ok": True, "id": uid})

        if path == "/reply":
            if not self.ok_auth(admin=True):
                return self.send_body(401, {"ok": False, "error": "unauthorized"})
            try:
                payload = json.loads(body.decode("utf-8"))
            except Exception:
                return self.send_body(400, {"ok": False, "error": "bad json"})
            with LOCK:
                data = read_json(REPLIES, {"version": 1, "replies": []})
                lesson = payload.get("lesson")
                if not lesson:
                    return self.send_body(400, {"ok": False, "error": "no lesson"})
                reps = [r for r in data.get("replies", []) if r.get("id") != lesson.get("id")]
                reps.insert(0, lesson)
                data["replies"] = reps[:60]
                data["version"] = int(data.get("version", 1)) + 1
                write_json(REPLIES, data)
            return self.send_body(200, {"ok": True, "version": data["version"]})

        if path == "/mark":
            if not self.ok_auth(admin=True):
                return self.send_body(401, {"ok": False, "error": "unauthorized"})
            try:
                payload = json.loads(body.decode("utf-8"))
            except Exception:
                return self.send_body(400, {"ok": False, "error": "bad json"})
            uid = payload.get("id", "")
            fp = os.path.join(INBOX, uid + ".json")
            if not os.path.isfile(fp):
                return self.send_body(404, {"ok": False, "error": "not found"})
            meta = read_json(fp, {})
            meta["status"] = payload.get("status", "done")
            write_json(fp, meta)
            return self.send_body(200, {"ok": True})

        return self.send_body(404, {"ok": False, "error": "no route", "path": path})


def main():
    ensure_dirs()
    srv = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    srv.daemon_threads = True
    print("studyhub listening on %d  content=%s data=%s" % (PORT, CONTENT_DIR, DATA_DIR), flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
