#!/bin/bash

set -eu

HOST="${PROD_HOST:-YOUR_SERVER_IP}"

URL="http://${HOST}:8080/health"

echo "========================================="
echo "Health Check"
echo "========================================="

echo "Checking:"
echo "${URL}"

for i in {1..10}
do

    if curl --fail --silent "${URL}" > /dev/null
    then

        echo ""
        echo "Health check successful."
        echo "Application is running."

        exit 0

    fi

    echo "Attempt ${i}/10 failed."

    sleep 5

done

echo ""
echo "Health check failed."

exit 1