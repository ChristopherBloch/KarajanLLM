#!/bin/bash
export PATH=/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:$PATH

echo "=== WEB PAGES ==="
for page in / /operations /heartbeat /security /models /services /dashboard /activities /performance; do
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 "http://localhost:5000${page}")
  echo "  ${page} -> ${code}"
done

echo "=== API ENDPOINTS ==="
for ep in /api/health /api/status /api/jobs/live /api/litellm/global-spend /api/security-events /api/records/thoughts /api/records/goals /api/schedule; do
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 "http://localhost:8000${ep}")
  echo "  ${ep} -> ${code}"
done

echo "=== CRON JOBS ==="
docker exec clawdbot openclaw cron list 2>/dev/null | head -20

echo "=== MLX INFERENCE TEST ==="
python3 /tmp/test_mlx.py 2>&1

echo "=== TRAEFIK ROUTING ==="
for path in / /api/health /operations /litellm-proxy; do
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 "http://localhost${path}")
  echo "  traefik${path} -> ${code}"
done

echo "=== DONE ==="
