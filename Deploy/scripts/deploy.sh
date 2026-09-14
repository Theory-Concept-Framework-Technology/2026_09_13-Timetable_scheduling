#!/bin/bash

set -eu

echo "========================================="
echo "School Timetable Deployment"
echo "========================================="

echo "Application : ${APP_NAME}"
echo "Image       : ${IMAGE_NAME}:${IMAGE_TAG}"
echo "Server      : ${PROD_HOST}"
echo "Deploy path : ${DEPLOY_PATH}"

echo ""
echo "Creating deployment directory..."

ssh root@"${PROD_HOST}" "
    mkdir -p '${DEPLOY_PATH}'
"

echo ""
echo "Copying Docker Compose file..."

scp docker-compose.yml \
    root@"${PROD_HOST}":"${DEPLOY_PATH}"/docker-compose.yml


echo ""
echo "Deploying container..."

ssh root@"${PROD_HOST}" bash <<EOF

set -eu

cd '${DEPLOY_PATH}'

export IMAGE_NAME='${IMAGE_NAME}'
export IMAGE_TAG='${IMAGE_TAG}'

echo "Pulling image..."

docker pull "\${IMAGE_NAME}:\${IMAGE_TAG}"

echo "Stopping old container..."

docker compose down || true

echo "Starting new container..."

docker compose up -d

echo "Removing unused images..."

docker image prune -f || true

echo "Deployment completed."

docker compose ps

EOF

echo "========================================="
echo "Deployment successful"
echo "========================================="