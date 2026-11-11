#!/usr/bin/env python3
"""删掉 Pangolin 里已停用域名的资源与记录（nyangley1762.org / warpdotsys.*）。"""
import shutil
import sqlite3
import subprocess

DB = "/opt/pangolin/config/db/db.sqlite"
DEAD_DOMAINS = ["mutj3wihmddy9z2", "7hy2yzybcoin15m", "slu3i5gjry8n2m1"]
RES_ID = 10  # Blog-WTX (nyangley1762.org)

subprocess.run(["docker", "stop", "traefik", "pangolin"], capture_output=True)
shutil.copy(DB, DB + ".bak-deaddomains")

c = sqlite3.connect(DB)
cur = c.cursor()
report = []

def run(sql, args=()):
    cur.execute(sql, args)
    report.append((sql.strip()[:60], cur.rowcount))

# 1) resource 10 的关联
run("delete from roleResources where resourceId=?", (RES_ID,))
run("delete from targets where resourceId=?", (RES_ID,))
run("delete from resourceRules where resourceId=?", (RES_ID,))
run("delete from requestAuditLog where resourceId=?", (RES_ID,))
run("delete from resources where resourceId=?", (RES_ID,))

# 2) 三个死域名
for did in DEAD_DOMAINS:
    run("delete from certificates where domainId=?", (did,))
    run("delete from dnsRecords where domainId=?", (did,))
    run("delete from dnsChallenges where domainId=?", (did,))
    run("delete from orgDomains where domainId=?", (did,))
    run("delete from resources where domainId=?", (did,))
    run("delete from domains where domainId=?", (did,))

c.commit()

# 3) 校验
left_res = list(cur.execute("select resourceId, name, fullDomain from resources where fullDomain like '%warpdotsys%' or fullDomain like '%nyangley%'"))
left_dom = list(cur.execute("select domainId, baseDomain from domains"))
c.close()

print("deleted:")
for s, n in report:
    if n:
        print("  ", s, "->", n)
print("剩余死域名资源:", left_res)
print("剩余 domains:", left_dom)

r = subprocess.run(["docker", "start", "pangolin"], capture_output=True, text=True)
print("start pangolin rc", r.returncode)
subprocess.run(["sleep", "12"])
r2 = subprocess.run(["docker", "start", "traefik"], capture_output=True, text=True)
print("start traefik rc", r2.returncode)
