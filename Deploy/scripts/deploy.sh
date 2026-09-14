#!/bin/bash
# Deploy School Timetable to the shared droplet (see Deploy/droplet.env.example).

set -eu

: "${PROD_HOST:?Set PROD_HOST (e.g. 143.244.128.22)}"
: "${DEPLOY_PATH:=/opt/school-timetable}"
: "${IMAGE_NAME:?Set IMAGE_NAME}"
: "${IMAGE_TAG:?Set IMAGE_TAG}"

COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-school-timetable}"
APP_PORT="${APP_PORT:-8090}"
APP_NAME="${APP_NAME:-school-timetable-fresh}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

echo "========================================="
echo "School Timetable Deployment"
echo "========================================="
echo "Application : ${APP_NAME}"
echo "Image       : ${IMAGE_NAME}:${IMAGE_TAG}"
echo "Server      : ${PROD_HOST}"
echo "Deploy path : ${DEPLOY_PATH}"
echo "Host port   : ${APP_PORT}"
echo "Compose -p  : ${COMPOSE_PROJECT_NAME}"
echo ""

ssh root@"${PROD_HOST}" "mkdir -p '${DEPLOY_PATH}'"

scp "${REPO_ROOT}/docker-compose.yml" \
    root@"${PROD_HOST}":"${DEPLOY_PATH}/docker-compose.yml"

ssh root@"${PROD_HOST}" bash <<EOF
set -eu
cd '${DEPLOY_PATH}'

export IMAGE_NAME='${IMAGE_NAME}'
export IMAGE_TAG='${IMAGE_TAG}'
export APP_PORT='${APP_PORT}'
export COMPOSE_PROJECT_NAME='${COMPOSE_PROJECT_NAME}'

echo "Pulling image..."
docker pull "\${IMAGE_NAME}:\${IMAGE_TAG}"

echo "Stopping old stack (project-scoped)..."
docker compose -p "\${COMPOSE_PROJECT_NAME}" -f docker-compose.yml down || true

echo "Starting container (${APP_PORT}:80)..."
docker compose -p "\${COMPOSE_PROJECT_NAME}" -f docker-compose.yml up -d

echo "Mild image cleanup (no -a / no volume prune)..."
docker image prune -f || true

docker compose -p "\${COMPOSE_PROJECT_NAME}" -f docker-compose.yml ps
EOF

echo ""
echo "Running remote health check..."
export PROD_HOST APP_PORT
bash "${SCRIPT_DIR}/healthcheck.sh"

echo "========================================="
echo "Deployment successful"
echo "URL: http://${PROD_HOST}:${APP_PORT}/"
echo "========================================="
