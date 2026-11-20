#!/bin/bash
# 在青岛服务器本机跑，绕开 SSH 会话被掐断的问题
LOG=/tmp/acme-study.log
: > "$LOG"
echo "=== start $(date) ===" >> "$LOG"

setsid ~/.acme.sh/acme.sh --issue \
  -d study.medwarp.com.cn \
  --webroot /var/www/html \
  --server letsencrypt \
  --keylength ec-256 >> "$LOG" 2>&1

echo "=== exit=$? $(date) ===" >> "$LOG"
