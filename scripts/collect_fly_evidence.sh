#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <FLY_APP_NAME>"
  exit 2
fi

APP="$1"
TS=$(date -u +%Y%m%dT%H%M%SZ)
OUTDIR="evidence/${APP}-${TS}"
mkdir -p "$OUTDIR"

echo "Collecting fly status..."
flyctl status --app "$APP" > "$OUTDIR/fly_status.txt" || true

echo "Collecting last logs..."
# Try --since first (newer flyctl), otherwise fallback to --num or plain logs
if flyctl logs --app "$APP" --since 10m > "$OUTDIR/fly_logs.txt" 2>/dev/null; then
  :
elif flyctl logs --app "$APP" --num 200 > "$OUTDIR/fly_logs.txt" 2>/dev/null; then
  :
else
  flyctl logs --app "$APP" > "$OUTDIR/fly_logs.txt" 2>/dev/null || true
fi

echo "Fetching endpoints..."
curl -sS "https://${APP}.fly.dev/ping" -o "$OUTDIR/ping_response.txt" || true
curl -sS -L https://cc-benigno-parra.fly.dev/metrics | head -n 200 > "$OUTDIR/metrics_response.txt" || true

echo "Evidence collected at: $OUTDIR"
