#!/usr/bin/env bash
set -e

echo "=== Running Pytest Unit Tests and Generating Reports ==="
mkdir -p reports
pytest -v --cov=ACEest_Fitness \
          --cov-report=term-missing \
          --cov-report=xml:reports/coverage.xml \
          --cov-report=html:reports/htmlcov \
          --junitxml=reports/test-results.xml

echo ""
echo "=== Tests Passed Successfully! ==="
echo "JUnit XML: reports/test-results.xml"
echo "Coverage XML: reports/coverage.xml"
echo "HTML Coverage Report: reports/htmlcov/index.html"
