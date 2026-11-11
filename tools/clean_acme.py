#!/usr/bin/env python3
"""清理 acme.json 里已停用域名（warpdotsys.* / nyangley1762.org）的证书条目。"""
import json
import shutil
import subprocess

P = "/opt/pangolin/config/letsencrypt/acme.json"
KEEP_SUFFIX = "medwarp.cn"

subprocess.run(["docker", "stop", "traefik"], capture_output=True)
shutil.copy(P, P + ".bak")

d = json.load(open(P))
total_before = 0
total_after = 0
for k, v in d.items():
    certs = v.get("Certificates") or []
    total_before += len(certs)
    kept = []
    dropped = []
    for c in certs:
        dom = c.get("domain") or {}
        main = dom.get("main") if isinstance(dom, dict) else str(dom)
        if main and main.endswith(KEEP_SUFFIX):
            kept.append(c)
        else:
            dropped.append(main)
    v["Certificates"] = kept
    total_after += len(kept)
    print("provider", k, "kept", [ (c.get('domain') or {}).get('main') for c in kept ])
    print("  dropped", dropped)

json.dump(d, open(P, "w"))
print("certs:", total_before, "->", total_after)

r = subprocess.run(["docker", "start", "traefik"], capture_output=True, text=True)
print("start rc", r.returncode, r.stderr[:200])
