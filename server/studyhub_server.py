#!/usr/bin/env python3
"""学习台 StudyHub 内容服务 + 账号

只依赖 Python 标准库。

公开（无需登录）：
  GET  /health
  GET  /manifest            课程树
  GET  /lesson?id=<id>      单节内容
  GET  /replies             答疑回复
  GET  /ipa/<name>          IPA / 页面分发

账号：
  POST /auth/register       {"username","password"}  —— 需 REGISTER_OPEN=1
  POST /auth/login          {"username","password"}  -> {"token","username"}
  GET  /auth/me             Authorization: Bearer <token>
  POST /auth/logout

进度（按用户隔离）：
  GET  /progress            当前用户进度
  POST /progress            合并保存 {"progress":{...},"wrongs":[...],"notes":{...},"stats":{...}}

管理：
  POST /upload, GET /inbox, POST /reply, POST /mark  —— 需要 admin 账号
"""
import hashlib
import hmac
import json
import os
import re
import secrets
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

DATA_DIR = os.environ.get("DATA_DIR", "/data")
CONTENT_DIR = os.environ.get("CONTENT_DIR", "/content")
PORT = int(os.environ.get("PORT", "8099"))
REGISTER_OPEN = os.environ.get("REGISTER_OPEN", "0") == "1"
MAX_UPLOAD = 25 * 1024 * 1024

INBOX = os.path.join(DATA_DIR, "inbox")
REPLIES = os.path.join(DATA_DIR, "replies.json")
USERS = os.path.join(DATA_DIR, "users.json")
SESSIONS = os.path.join(DATA_DIR, "sessions.json")
PROGRESS_DIR = os.path.join(DATA_DIR, "progress")
IPA_DIR = os.environ.get("IPA_DIR", os.path.join(DATA_DIR, "ipa"))
WEB_DIR = os.environ.get("WEB_DIR", "/opt/studyhub/web")
TLS_CERT = os.environ.get("TLS_CERT", "")
TLS_KEY = os.environ.get("TLS_KEY", "")
LOCK = threading.Lock()

# 长轮询等待者：username -> set(Event)。push 时直接唤醒，避免轮询文件。
WAITERS = {}
WAITER_LOCK = threading.Lock()


def register_waiter(user):
    ev = threading.Event()
    with WAITER_LOCK:
        WAITERS.setdefault(user, set()).add(ev)
    return ev


def drop_waiter(user, ev):
    with WAITER_LOCK:
        s = WAITERS.get(user)
        if s:
            s.discard(ev)
            if not s:
                WAITERS.pop(user, None)


def notify_waiters(user):
    with WAITER_LOCK:
        for ev in list(WAITERS.get(user, ())):
            ev.set()

SAFE_ID = re.compile(r"^[A-Za-z0-9_\-/\.]{1,120}$")
SAFE_USER = re.compile(r"^[A-Za-z0-9_\-]{3,32}$")


def ensure_dirs():
    for d in (INBOX, PROGRESS_DIR, IPA_DIR):
        os.makedirs(d, exist_ok=True)


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


# ---------- 密码与会话 ----------

def hash_password(password, salt=None):
    salt = salt or secrets.token_hex(16)
    dk = hashlib.scrypt(password.encode("utf-8"), salt=salt.encode("utf-8"),
                        n=16384, r=8, p=1, dklen=32)
    return salt, dk.hex()


def verify_password(password, salt, expected):
    _, got = hash_password(password, salt)
    return hmac.compare_digest(got, expected)


def load_users():
    return read_json(USERS, {})


def save_users(u):
    write_json(USERS, u)


def load_sessions():
    return read_json(SESSIONS, {})


def save_sessions(s):
    write_json(SESSIONS, s)


def new_session(username):
    token = secrets.token_urlsafe(32)
    with LOCK:
        s = load_sessions()
        # 清掉 30 天前的会话
        now = time.time()
        s = {k: v for k, v in s.items() if now - v.get("created", 0) < 30 * 86400}
        s[token] = {"username": username, "created": now}
        save_sessions(s)
    return token


def user_from_token(token):
    if not token:
        return None
    s = load_sessions()
    rec = s.get(token)
    if not rec:
        return None
    return rec.get("username")


def progress_file(username):
    return os.path.join(PROGRESS_DIR, username + ".json")


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
    server_version = "StudyHub/2.0"
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
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def token(self):
        h = self.headers.get("Authorization", "")
        return h[7:].strip() if h.startswith("Bearer ") else ""

    def ok_admin(self):
        """管理员 = users.json 里 role 为 admin 的账号"""
        u = self.current_user()
        if not u:
            return False
        rec = load_users().get(u, {})
        return rec.get("role") == "admin"

    def current_user(self):
        return user_from_token(self.token())

    def read_json_body(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n > MAX_UPLOAD:
            return None, None
        body = self.rfile.read(n) if n else b""
        try:
            return json.loads(body.decode("utf-8")), body
        except Exception:
            return None, body

    def do_OPTIONS(self):
        return self.send_body(204, b"")

    # ---------- GET ----------
    def do_GET(self):
        u = urlparse(self.path)
        path = u.path
        qs = parse_qs(u.query)

        if path in ("/health", "/"):
            return self.send_body(200, {"ok": True, "service": "studyhub",
                                        "version": 2, "time": int(time.time())})

        # 课程与题目：公开
        if path == "/manifest":
            m = read_json(os.path.join(CONTENT_DIR, "manifest.json"), None)
            if m is None:
                return self.send_body(500, {"ok": False, "error": "manifest missing"})
            return self.send_body(200, m)

        if path == "/lesson":
            lid = (qs.get("id") or [""])[0]
            p = lesson_path(lid)
            if not p:
                return self.send_body(404, {"ok": False, "error": "lesson not found", "id": lid})
            return self.send_body(200, read_json(p, {}))

        if path == "/replies":
            data = read_json(REPLIES, {"version": 1, "replies": []})
            return self.send_body(200, data)

        # 账号
        if path == "/auth/me":
            user = self.current_user()
            if not user:
                return self.send_body(401, {"ok": False, "error": "unauthorized"})
            users = load_users()
            rec = users.get(user, {})
            return self.send_body(200, {"ok": True, "username": user,
                                        "created": rec.get("created", 0),
                                        "role": rec.get("role", "user"),
                                        "registerOpen": REGISTER_OPEN})

        if path == "/auth/config":
            return self.send_body(200, {"ok": True, "registerOpen": REGISTER_OPEN})

        # 进度
        if path == "/progress":
            user = self.current_user()
            if not user:
                return self.send_body(401, {"ok": False, "error": "unauthorized"})
            data = read_json(progress_file(user), {"progress": {}, "wrongs": [], "notes": {}, "stats": {}})
            return self.send_body(200, {"ok": True, "username": user, "data": data})

        # 长轮询：等到进度有变化或超时才返回，配合客户端循环实现秒级一致
        if path == "/progress/poll":
            user = self.current_user()
            if not user:
                return self.send_body(401, {"ok": False, "error": "unauthorized"})
            try:
                since = float((qs.get("since") or ["0"])[0])
            except Exception:
                since = 0.0
            fp = progress_file(user)
            # 先看有没有已经发生的变化
            data = read_json(fp, {"progress": {}, "wrongs": {}, "notes": {}, "stats": {}})
            if float(data.get("updated") or 0) > since:
                return self.send_body(200, {"ok": True, "username": user,
                                            "updated": data.get("updated") or 0,
                                            "data": data})
            # 没有变化就挂起，等 push 唤醒（最多 25 秒）
            ev = register_waiter(user)
            try:
                ev.wait(timeout=25.0)
            finally:
                drop_waiter(user, ev)
            data = read_json(fp, {"progress": {}, "wrongs": [], "notes": {}, "stats": {}})
            changed = float(data.get("updated") or 0) > since
            return self.send_body(200, {"ok": True, "username": user,
                                        "updated": data.get("updated") or 0,
                                        "data": data if changed else None})

        # 网页版静态资源：不带 /web 前缀也认（浏览器会把相对路径解析到根）
        if path in ("/app.css", "/app.js") or path.startswith("/vendor/") or path.startswith("/katex/"):
            path = "/web" + path

        # 访问 /web 时重定向到 /web/，保证相对路径基准正确
        if path == "/web":
            self.send_response(301)
            self.send_header("Location", "/web/")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return

        # 网页版（静态 SPA）
        if path == "/web" or path.startswith("/web/"):
            rel = path[5:].lstrip("/") or "index.html"
            if ".." in rel or rel.startswith("/"):
                return self.send_body(400, {"ok": False, "error": "bad path"})
            fp = os.path.join(WEB_DIR, rel)
            if os.path.isdir(fp):
                fp = os.path.join(fp, "index.html")
            if not os.path.isfile(fp):
                return self.send_body(404, {"ok": False, "error": "not found", "path": rel})
            with open(fp, "rb") as f:
                data = f.read()
            low = fp.lower()
            if low.endswith(".html"):
                ctype = "text/html; charset=utf-8"
            elif low.endswith(".js"):
                ctype = "application/javascript; charset=utf-8"
            elif low.endswith(".css"):
                ctype = "text/css; charset=utf-8"
            elif low.endswith(".woff2"):
                ctype = "font/woff2"
            elif low.endswith(".woff"):
                ctype = "font/woff"
            elif low.endswith(".ttf"):
                ctype = "font/ttf"
            elif low.endswith(".png"):
                ctype = "image/png"
            elif low.endswith(".svg"):
                ctype = "image/svg+xml"
            else:
                ctype = "application/octet-stream"
            return self.send_body(200, data, ctype)

        if path.startswith("/ipa/"):
            name = path.split("/")[-1]
            if not re.match(r"^[A-Za-z0-9_\-\.]{1,120}$", name):
                return self.send_body(400, {"ok": False, "error": "bad name"})
            fp = os.path.join(IPA_DIR, name)
            if not os.path.isfile(fp):
                return self.send_body(404, {"ok": False, "error": "not found", "name": name})
            with open(fp, "rb") as f:
                data = f.read()
            low = name.lower()
            if low.endswith(".html"):
                ctype = "text/html; charset=utf-8"
            elif low.endswith(".json"):
                ctype = "application/json; charset=utf-8"
            elif low.endswith(".png"):
                ctype = "image/png"
            elif low.endswith(".plist"):
                ctype = "application/xml; charset=utf-8"
            else:
                ctype = "application/octet-stream"
            return self.send_body(200, data, ctype)

        if path == "/inbox":
            if not self.ok_admin():
                return self.send_body(401, {"ok": False, "error": "unauthorized"})
            items = []
            for fn in sorted(os.listdir(INBOX), reverse=True):
                if fn.endswith(".json"):
                    items.append(read_json(os.path.join(INBOX, fn), {}))
            return self.send_body(200, {"inbox": items[:100]})

        if path.startswith("/inbox/file/"):
            if not self.ok_admin():
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
            low = name.lower()
            if low.endswith((".jpg", ".jpeg")):
                ctype = "image/jpeg"
            elif low.endswith(".png"):
                ctype = "image/png"
            elif low.endswith(".pdf"):
                ctype = "application/pdf"
            return self.send_body(200, data, ctype)

        return self.send_body(404, {"ok": False, "error": "no route", "path": path})

    # ---------- POST ----------
    def do_POST(self):
        u = urlparse(self.path)
        path = u.path

        if path == "/auth/register":
            payload, _ = self.read_json_body()
            if payload is None:
                return self.send_body(400, {"ok": False, "error": "bad json"})
            if not REGISTER_OPEN:
                return self.send_body(403, {"ok": False, "error": "register_closed",
                                            "message": "注册暂未开放"})
            username = (payload.get("username") or "").strip()
            password = payload.get("password") or ""
            if not SAFE_USER.match(username):
                return self.send_body(400, {"ok": False, "error": "用户名需 3-32 位字母数字下划线连字符"})
            if len(password) < 6:
                return self.send_body(400, {"ok": False, "error": "密码至少 6 位"})
            with LOCK:
                users = load_users()
                if username in users:
                    return self.send_body(409, {"ok": False, "error": "用户名已存在"})
                salt, h = hash_password(password)
                users[username] = {"salt": salt, "hash": h,
                                   "created": int(time.time()), "role": "user"}
                save_users(users)
            token = new_session(username)
            return self.send_body(200, {"ok": True, "token": token, "username": username})

        if path == "/auth/login":
            payload, _ = self.read_json_body()
            if payload is None:
                return self.send_body(400, {"ok": False, "error": "bad json"})
            username = (payload.get("username") or "").strip()
            password = payload.get("password") or ""
            users = load_users()
            rec = users.get(username)
            if not rec or not verify_password(password, rec.get("salt", ""), rec.get("hash", "")):
                # 统一延迟，避免用户名枚举
                time.sleep(0.35)
                return self.send_body(401, {"ok": False, "error": "用户名或密码错误"})
            token = new_session(username)
            return self.send_body(200, {"ok": True, "token": token, "username": username})

        if path == "/auth/logout":
            t = self.token()
            if t:
                with LOCK:
                    s = load_sessions()
                    s.pop(t, None)
                    save_sessions(s)
            return self.send_body(200, {"ok": True})

        if path == "/progress":
            user = self.current_user()
            if not user:
                return self.send_body(401, {"ok": False, "error": "unauthorized"})
            payload, _ = self.read_json_body()
            if payload is None:
                return self.send_body(400, {"ok": False, "error": "bad json"})
            fp = progress_file(user)
            with LOCK:
                cur = read_json(fp, {"progress": {}, "wrongs": [], "notes": {}, "stats": {}})
                # progress / notes：按 key 合并
                for k in ("progress", "notes"):
                    if isinstance(payload.get(k), dict):
                        cur.setdefault(k, {}).update(payload[k])
                # wrongs：按 id 去重合并
                if isinstance(payload.get("wrongs"), list):
                    have = {w.get("id") for w in cur.get("wrongs", []) if isinstance(w, dict)}
                    for w in payload["wrongs"]:
                        if isinstance(w, dict) and w.get("id") not in have:
                            cur.setdefault("wrongs", []).append(w)
                            have.add(w.get("id"))
                # stats：覆盖
                if isinstance(payload.get("stats"), dict):
                    cur["stats"] = payload["stats"]
                cur["updated"] = time.time()
                write_json(fp, cur)
            notify_waiters(user)
            return self.send_body(200, {"ok": True, "count": len(cur.get("wrongs", []))})

        if path == "/upload":
            n = int(self.headers.get("Content-Length") or 0)
            if n > MAX_UPLOAD:
                return self.send_body(413, {"ok": False, "error": "too large"})
            body = self.rfile.read(n) if n else b""
            if not (self.ok_admin() or self.current_user()):
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
                "from": self.current_user() or "admin",
            }
            write_json(os.path.join(INBOX, uid + ".json"), meta)
            print("[upload] %s %s %d bytes" % (stored, fname, len(fdata)), flush=True)
            return self.send_body(200, {"ok": True, "id": uid})

        if path == "/reply":
            if not self.ok_admin():
                return self.send_body(401, {"ok": False, "error": "unauthorized"})
            payload, _ = self.read_json_body()
            if payload is None:
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
            if not self.ok_admin():
                return self.send_body(401, {"ok": False, "error": "unauthorized"})
            payload, _ = self.read_json_body()
            if payload is None:
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
    scheme = "http"
    if TLS_CERT and TLS_KEY and os.path.isfile(TLS_CERT) and os.path.isfile(TLS_KEY):
        import ssl
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        ctx.load_cert_chain(TLS_CERT, TLS_KEY)
        srv.socket = ctx.wrap_socket(srv.socket, server_side=True)
        scheme = "https"
    print("studyhub v2 listening on %s://0.0.0.0:%d  content=%s data=%s registerOpen=%s"
          % (scheme, PORT, CONTENT_DIR, DATA_DIR, REGISTER_OPEN), flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
