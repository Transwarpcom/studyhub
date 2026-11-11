#!/usr/bin/env python3
"""把 Pangolin 的 Cloudflare DNS token 换成有 medwarp.cn 权限的那个，并重建 traefik。"""
import re
import shutil
import subprocess

P = "/opt/pangolin/docker-compose.yml"
NEW = "cfut_QOpWZZZ9PLACEHOLDER"

s = open(P).read()
shutil.copy(P, P + ".bak")
s2 = re.sub(r'CLOUDFLARE_DNS_API_TOKEN:\s*"[^"]*"',
            'CLOUDFLARE_DNS_API_TOKEN: "%s"' % NEW, s)
open(P, "w").write(s2)
print("token replaced:", ("%s" % NEW) in s2)

r = subprocess.run(["docker", "compose", "up", "-d", "traefik"],
                   cwd="/opt/pangolin", capture_output=True, text=True)
print("compose rc:", r.returncode)
print(r.stdout[-400:])
print(r.stderr[-400:])
