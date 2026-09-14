#!/bin/bash
# GET /health on the host-mapped port (container nginx listens on 80).

set -eu

: "${PROD_HOST:?Set PROD_HOST}"

APP_PORT="${APP_PORT:-8090}"
URL="http://${PROD_HOST}:${APP_PORT}/health"

echo "========================================="
echo "Health Check"
echo "========================================="
echo "Checking: ${URL}"

for i in $(seq 1 10); do
    if curl --fail --silent "${URL}" > /dev/null; then
        echo ""
        echo "Health check successful."
        exit 0
    fi
    echo "Attempt ${i}/10 failed."
    sleep 5
done

echo ""
echo "Health check failed."
exit 1
