#!/usr/bin/env bash
# Script to demonstrate instantaneous Blue-Green traffic cutover and rollback

TARGET_COLOR=${1:-green}

echo "Switching active traffic on Service aceest-bluegreen-service to color: ${TARGET_COLOR}..."
kubectl patch service aceest-bluegreen-service -n aceest-fitness -p '{"spec":{"selector":{"color":"'"${TARGET_COLOR}"'"}}}'

echo "Traffic successfully switched! Verifying current active endpoint:"
kubectl get service aceest-bluegreen-service -n aceest-fitness -o jsonpath='{.spec.selector}'
echo ""
