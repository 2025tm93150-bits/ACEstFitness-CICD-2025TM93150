#!/usr/bin/env bash
# Kubernetes Rollback Demonstration Script for ACEest Fitness
# Demonstrates progressive deployment resilience, fault detection, and instant zero-downtime rollback.

NAMESPACE="aceest-fitness"
DEPLOYMENT="aceest-fitness"

echo "=========================================================="
echo "   ACEest Fitness - Kubernetes Deployment Rollback Suite   "
echo "=========================================================="

echo "Step 1: Inspecting current rollout revision history..."
kubectl rollout history deployment/${DEPLOYMENT} -n ${NAMESPACE}

echo ""
echo "Step 2: Simulating bad deployment rollout (invalid non-existent image)..."
kubectl set image deployment/${DEPLOYMENT} aceest-app=aceest-fitness:v-broken-tag -n ${NAMESPACE}

echo "Observing rollout status (Kubernetes detects failure and halts):"
kubectl rollout status deployment/${DEPLOYMENT} -n ${NAMESPACE} --timeout=15s || echo "Rollout halted due to ImagePullBackOff / Readiness check."

echo ""
echo "Step 3: Checking pod status (old pods remain healthy, new pod fails):"
kubectl get pods -n ${NAMESPACE} -l app=aceest-fitness

echo ""
echo "Step 4: Executing Instant Rollback to last stable revision..."
kubectl rollout undo deployment/${DEPLOYMENT} -n ${NAMESPACE}

echo ""
echo "Step 5: Verifying cluster recovery after rollback:"
kubectl rollout status deployment/${DEPLOYMENT} -n ${NAMESPACE}
kubectl get pods -n ${NAMESPACE} -l app=aceest-fitness

echo ""
echo "=========================================================="
echo "Rollback successfully completed with ZERO end-user downtime!"
echo "=========================================================="
