#!/bin/bash
# Run on the Ubuntu server inside the weburbs deploy folder:
#   chmod +x scripts/check-simulation.sh
#   ./scripts/check-simulation.sh 45288f46-75b8-46d7-8977-56660cd9498e
set -euo pipefail

SIM="${1:-}"
if [ -z "$SIM" ]; then
  echo "Usage: $0 <simulation-uuid>"
  echo "Example: $0 45288f46-75b8-46d7-8977-56660cd9498e"
  exit 1
fi

cd "$(dirname "$0")/.."
echo "=== docker compose (pwd: $(pwd)) ==="
docker compose ps

echo ""
echo "=== backend: simulation fixes present? ==="
docker compose exec -T backend sh -c '
  grep -n "load_from_disk" /app/projects/api/simulate.py || echo "MISSING load_from_disk — rebuild backend from updated source"
'

echo ""
echo "=== optimizer: callback.json support present? ==="
docker compose exec -T optimizer sh -c '
  grep -n "load_from_disk" /app/server.py 2>/dev/null || grep -n "_post_callback" /app/server.py 2>/dev/null || echo "MISSING server.py fixes — rebuild optimizer from ../urbs-weburbs"
'

echo ""
echo "=== shared volume /app/result ==="
docker compose exec -T backend sh -c "ls -la /app/result 2>&1 || echo 'NO /app/result on backend'"
docker compose exec -T optimizer sh -c "ls -la /app/result 2>&1 || echo 'NO /app/result on optimizer'"

echo ""
echo "=== files for sim $SIM ==="
docker compose exec -T backend sh -c "find /app/result -path '*${SIM}*' -ls 2>/dev/null || echo 'No files on backend'"
docker compose exec -T optimizer sh -c "find /app/result -path '*${SIM}*' -ls 2>/dev/null || echo 'No files on optimizer'"

echo ""
echo "=== callback.json status (optimizer) ==="
docker compose exec -T optimizer sh -c "
  f=\$(find /app/result -path '*${SIM}*/callback.json' | head -1)
  if [ -n \"\$f\" ]; then
    python3 -c \"import json; d=json.load(open('\$f')); print('status:', d.get('status')); print('data keys:', list((d.get('data') or {}).keys())); print('log chars:', len(d.get('log') or ''))\"
  else
    echo 'callback.json not found on optimizer'
  fi
"

echo ""
echo "=== database row ==="
docker compose exec -T db psql -U urbs -d urbs -c \
  "SELECT id, completed, status, length(log) AS log_len, result IS NOT NULL AS has_result FROM projects_simulationresult WHERE id='${SIM}';"

echo ""
echo "=== backend logs (callback / missing file) ==="
docker compose logs backend --tail=80 2>&1 | grep -E "callback|${SIM}|load_from_disk|report_simulation" || true

echo ""
echo "=== optimizer logs (errors) ==="
docker compose logs optimizer --tail=80 2>&1 | grep -iE "error|traceback|failed|callback" || true

echo ""
echo "=== If fixes MISSING, run on Ubuntu: ==="
echo "  rsync/copy weburbs + urbs-weburbs from your Windows machine"
echo "  docker compose up -d --build optimizer backend"
