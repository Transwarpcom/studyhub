#!/usr/bin/env python3
"""为 Pangolin 插入一条临时 Integration API key（sha256 存储），用于走 API 删死域名。"""
import hashlib
import secrets
import sqlite3
import subprocess
import time

DB = "/opt/pangolin/config/db/db.sqlite"

key = "pgn_" + secrets.token_urlsafe(32).lower().replace("-", "x").replace("_", "y")
key = key[:48]
digest = hashlib.sha256(key.lower().encode()).hexdigest()

subprocess.run(["docker", "stop", "traefik"], capture_output=True)
time.sleep(1)

c = sqlite3.connect(DB)
c.execute(
    "insert into apiKeys (apiKeyId, name, apiKeyHash, lastChars, dateCreated, isRoot) "
    "values (?, ?, ?, ?, ?, ?)",
    (secrets.token_hex(12), "hermes-temp", digest, key[-4:], int(time.time() * 1000), 1),
)
c.commit()
n = c.execute("select count(*) from apiKeys").fetchone()[0]
c.close()

subprocess.run(["docker", "start", "traefik"], capture_output=True)

# 只把 key 写到服务器本地临时文件，不回显
open("/tmp/.pg_key", "w").write(key)
import os
os.chmod("/tmp/.pg_key", 0o600)

print("inserted apiKeys rows:", n, "hash prefix:", digest[:12], "key len:", len(key))
