# -*- coding: utf-8 -*-
"""服务端：/health 带网页版指纹；App：日志接入"""
import io

ROOT = r"C:/Users/chong/Documents/studyhub/"


def sub(path, old, new, tag):
    p = ROOT + path
    s = io.open(p, encoding="utf-8").read()
    n = s.count(old)
    assert n == 1, "%s: %s 命中 %d" % (path, tag, n)
    io.open(p, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
    print("  ok", path, "|", tag)


# ---------- 服务端 web 指纹 ----------
sub("server/studyhub_server.py",
    """WEB_DIR = os.environ.get("WEB_DIR", "/opt/studyhub/web")""",
    """WEB_DIR = os.environ.get("WEB_DIR", "/opt/studyhub/web")


def web_fingerprint():
    \"\"\"网页版 app.js 的指纹（前 8 位），客户端据此判断网页版是否换过\"\"\"
    try:
        import hashlib
        p = os.path.join(WEB_DIR, "app.js")
        with open(p, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()[:8]
    except Exception:
        return \"\"""", "web_fingerprint")

sub("server/studyhub_server.py",
    """        if path == "/health":
            return self.send_body(200, {"ok": True, "service": "studyhub",
                                        "version": 2, "time": int(time.time())})""",
    """        if path == "/health":
            m = read_json(os.path.join(CONTENT_DIR, "manifest.json"), {}) or {}
            return self.send_body(200, {"ok": True, "service": "studyhub",
                                        "version": 2, "time": int(time.time()),
                                        "web": web_fingerprint(),
                                        "content": m.get("version")})""", "health 字段")

# ---------- App：错误写日志 ----------
sub("Sources/Store.swift",
    """            } catch {
                lastError = error.localizedDescription""",
    """            } catch {
                lastError = error.localizedDescription
                Log.add("刷新失败：\\(error.localizedDescription)")""", "刷新失败日志")

sub("Sources/Store.swift",
    """        } catch {
            if force { lastError = error.localizedDescription }""",
    """        } catch {
            Log.add("载入失败 \\(node.id)：\\(error.localizedDescription)")
            if force { lastError = error.localizedDescription }""", "载入失败日志")

print("done")
