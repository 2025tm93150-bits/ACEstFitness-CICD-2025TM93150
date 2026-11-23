#!/usr/bin/env bash
# Script to easily deploy and demonstrate each progressive deployment strategy in Kubernetes / Minikube

STRATEGY=${1:-"all"}

echo "=== ACEest Fitness - Kubernetes Deployment Manager ==="
echo "Selected Strategy: ${STRATEGY}"

# Create namespace & config
kubectl apply -f k8s/01-namespace.yaml
kubectl apply -f k8s/02-configmap.yaml

case ${STRATEGY} in
  rolling)
    echo "Deploying Rolling Update..."
    kubectl apply -f k8s/03-rolling-update/
    kubectl rollout status deployment/aceest-fitness -n aceest-fitness
    ;;
  blue-green)
    echo "Deploying Blue-Green Environments..."
    kubectl apply -f k8s/04-blue-green/
    kubectl get pods -n aceest-fitness -l app=aceest-bluegreen --show-labels
    ;;
  canary)
    echo "Deploying Canary Split (80/20)..."
    kubectl apply -f k8s/05-canary/
    kubectl get pods -n aceest-fitness -l app=aceest-canary-demo --show-labels
    ;;
  shadow)
    echo "Deploying Shadow Mirroring..."
    kubectl apply -f k8s/06-shadow/
    kubectl get pods -n aceest-fitness -l app=aceest-shadow-demo --show-labels
    ;;
  ab-testing)
    echo "Deploying A/B Cohort Routing..."
    kubectl apply -f k8s/07-ab-testing/
    kubectl get pods -n aceest-fitness -l app=aceest-ab-testing --show-labels
    ;;
  all)
    echo "Deploying all strategies into aceest-fitness namespace..."
    kubectl apply -f k8s/03-rolling-update/
    kubectl apply -f k8s/04-blue-green/
    kubectl apply -f k8s/05-canary/
    kubectl apply -f k8s/06-shadow/
    kubectl apply -f k8s/07-ab-testing/
    echo ""
    echo "All manifests applied. Current pods in cluster:"
    kubectl get pods -n aceest-fitness
    ;;
  *)
    echo "Usage: $0 [rolling|blue-green|canary|shadow|ab-testing|all]"
    exit 1
    ;;
esac
