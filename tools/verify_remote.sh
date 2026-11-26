#!/bin/bash
cd /opt/studyhub/content/lessons || exit 1
for f in math_6-1 math_6-2 math_6-3 math_hwb-6-1 math_hwb-6-2a math_hwb-6-2b math_hwb-6-3 math_test-1 math_test-2 math_test-3 math_test-4 math_test-5 math_test-6; do
  if [ ! -f "$f.json" ]; then
    printf '%-18s MISSING\n' "$f"
    continue
  fi
  printf '%-18s %7s bytes  ' "$f" "$(stat -c%s "$f.json")"
  python3 - "$f.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1], encoding='utf-8'))
nq = len([c for c in d['cards'] if c.get('type') != 'lecture'])
print('id=%s cards=%d quiz=%d' % (d['id'], len(d['cards']), nq))
PY
done
echo "--- manifest ---"
python3 - <<'PY'
import json
m = json.load(open('/opt/studyhub/content/manifest.json', encoding='utf-8'))
print('version =', m['version'], 'updated =', m['updated'])
def cnt(n):
    n_lesson = 1 if n.get('kind') == 'lesson' else 0
    for c in n.get('children') or []:
        n_lesson += cnt(c)
    return n_lesson
for c in m['tree']:
    print('%-14s lessons=%d' % (c['title'], cnt(c)))
PY
