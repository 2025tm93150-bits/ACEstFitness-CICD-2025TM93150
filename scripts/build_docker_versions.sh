#!/usr/bin/env bash
# Script to build and tag all application versions for Docker Hub repository
# Usage: ./scripts/build_docker_versions.sh <your-dockerhub-username>

DOCKERHUB_USER=${1:-"mydevopsuser"}
IMAGE_NAME="${DOCKERHUB_USER}/aceest-fitness"

echo "============================================================"
echo " Building Docker Images for ACEest Fitness Across All Versions"
echo " Target Repository: ${IMAGE_NAME}"
echo "============================================================"

# Build version 1.0
echo "--> Building v1.0..."
docker build --build-arg APP_FILE=ACEest_Fitness_v1.0.py -t ${IMAGE_NAME}:v1.0 -t ${IMAGE_NAME}:1.0.0 .

# Build version 1.1
echo "--> Building v1.1..."
docker build --build-arg APP_FILE=ACEest_Fitness_v1.1.py -t ${IMAGE_NAME}:v1.1 -t ${IMAGE_NAME}:1.1.0 .

# Build version 2.0
echo "--> Building v2.0..."
docker build --build-arg APP_FILE=ACEest_Fitness_v2.0.py -t ${IMAGE_NAME}:v2.0 -t ${IMAGE_NAME}:2.0.0 .

# Build version 3.0 (Flagship Release)
echo "--> Building v3.0 (Latest)..."
docker build -t ${IMAGE_NAME}:v3.0 -t ${IMAGE_NAME}:3.0.0 -t ${IMAGE_NAME}:latest .

echo ""
echo "=== All Docker Images Built Successfully ==="
docker images | grep ${IMAGE_NAME} || docker images | grep aceest-fitness

echo ""
echo "To push these images to your Docker Hub repository, run:"
echo "docker login"
echo "docker push ${IMAGE_NAME}:v1.0"
echo "docker push ${IMAGE_NAME}:v1.1"
echo "docker push ${IMAGE_NAME}:v2.0"
echo "docker push ${IMAGE_NAME}:v3.0"
echo "docker push ${IMAGE_NAME}:latest"
