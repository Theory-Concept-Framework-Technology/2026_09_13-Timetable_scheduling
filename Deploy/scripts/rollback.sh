#!/bin/bash

set +e

echo "========================================="
echo "Rollback"
echo "========================================="

ssh root@"${PROD_HOST}" bash <<EOF

cd '${DEPLOY_PATH}'

echo "Stopping current deployment..."

docker compose down || true

echo "Looking for previous timetable image..."

docker images '${IMAGE_NAME}' --format '{{.Tag}}' | head -10

echo ""
echo "Rollback requires IMAGE_TAG to point to"
echo "a previously successful Docker image."

EOF

echo "Rollback procedure completed."