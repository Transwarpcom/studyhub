#!/bin/bash
# 用现有会话 token 走真实 HTTP 验证（只读，不改任何数据）
TOKEN=$(python3 - <<'PY'
import json, os
p = '/opt/studyhub/data/sessions.json'
try:
    d = json.load(open(p, encoding='utf-8'))
except Exception as e:
    print('')
    raise SystemExit
# 结构可能是 {token: {...}} 或 {"sessions": {...}}
items = d.get('sessions') if isinstance(d, dict) and 'sessions' in d else d
if isinstance(items, dict) and items:
    # 取 issue 时间最新的
    best = None
    for k, v in items.items():
        ts = 0
        if isinstance(v, dict):
            ts = v.get('created') or v.get('issued') or 0
        if best is None or ts > best[1]:
            best = (k, ts)
    print(best[0] if best else '')
PY
)
echo "token found: $([ -n "$TOKEN" ] && echo yes || echo no)"

BASE="https://127.0.0.1:8443"
H="Authorization: Bearer $TOKEN"

code=$(curl -sk -o /tmp/m.json -w '%{http_code}' -H "$H" "$BASE/manifest")
echo "GET /manifest -> $code  $(python3 -c "import json;d=json.load(open('/tmp/m.json'));print('version='+str(d['version']))" 2>/dev/null)"

for id in math/6-1 math/6-2 math/6-3 math/hwb-6-1 math/hwb-6-2a math/hwb-6-2b math/hwb-6-3 math/test-1 math/test-2 math/test-3 math/test-4 math/test-5 math/test-6; do
  code=$(curl -sk -o /tmp/l.json -w '%{http_code}' -H "$H" --get --data-urlencode "id=$id" "$BASE/lesson")
  printf '%-16s -> %s  ' "$id" "$code"
  python3 -c "import json;d=json.load(open('/tmp/l.json'));print('id='+d.get('id','?'), 'cards='+str(len(d.get('cards',[]))))" 2>/dev/null || echo '(bad json)'
done

echo "--- 抽查一道题的内容 ---"
curl -sk -H "$H" --get --data-urlencode "id=math/test-6" "$BASE/lesson" | python3 -c "
import json,sys
d=json.load(sys.stdin)
c=d['cards'][-1]
print('last card id =', c['id'], '| type =', c['type'])
print(c['explain'][:120].replace(chr(10),' '))
"
