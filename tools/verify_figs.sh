#!/bin/bash
# 验证：内容里带 svg、网页版能渲染 svg、看解析按钮在
TOKEN=$(python3 - <<'PY'
import json
d = json.load(open('/opt/studyhub/data/sessions.json', encoding='utf-8'))
items = d.get('sessions') if isinstance(d, dict) and 'sessions' in d else d
best = None
for k, v in (items or {}).items():
    ts = (v or {}).get('created') or (v or {}).get('issued') or 0 if isinstance(v, dict) else 0
    if best is None or ts > best[1]:
        best = (k, ts)
print(best[0] if best else '')
PY
)
BASE="https://127.0.0.1:8443"
H="Authorization: Bearer $TOKEN"

echo "--- lesson 里的 svg ---"
for id in math/6-2 math/hwb-6-1 math/hwb-6-3 math/test-6; do
  curl -sk -H "$H" --get --data-urlencode "id=$id" "$BASE/lesson" | python3 -c "
import json,sys
d=json.load(sys.stdin)
n=sum(1 for c in d['cards'] if c.get('svg'))
print('%-16s cards=%d svg=%d' % (d['id'], len(d['cards']), n))
"
done

echo "--- 网页版静态文件 ---"
curl -sk -o /tmp/app.js -w 'app.js %{http_code} %{size_download}\n' "$BASE/web/app.js"
grep -c 'figure' /tmp/app.js | xargs echo '  app.js 里 figure 出现次数:'
grep -c 'peekbtn' /tmp/app.js | xargs echo '  app.js 里 peekbtn 出现次数:'
curl -sk -o /tmp/app.css -w 'app.css %{http_code} %{size_download}\n' "$BASE/web/app.css"
grep -c 'figure svg' /tmp/app.css | xargs echo '  app.css 里 .figure svg:'

echo "--- manifest ---"
curl -sk -H "$H" "$BASE/manifest" | python3 -c "import json,sys;d=json.load(sys.stdin);print('version',d['version'])"
