#!/bin/bash
# Test script for Pulp Hugging Face plugin API endpoints

set -e

BASE_URL="http://localhost:5001"
AUTH="admin:password"

echo "=== Testing Pulp Hugging Face Plugin API Endpoints ==="
echo

echo "1. Testing Hugging Face Remotes endpoint..."
curl -s -u "$AUTH" "$BASE_URL/pulp/api/v3/remotes/hugging_face/hugging-face/" | python3 -c "import sys, json; print('✅ Remotes endpoint working') if json.load(sys.stdin) else print('❌ Failed')"

echo "2. Testing Hugging Face Distributions endpoint..."
curl -s -u "$AUTH" "$BASE_URL/pulp/api/v3/distributions/hugging_face/hugging-face/" | python3 -c "import sys, json; print('✅ Distributions endpoint working') if json.load(sys.stdin) else print('❌ Failed')"

echo "3. Testing Hugging Face Content endpoint..."
curl -s -u "$AUTH" "$BASE_URL/pulp/api/v3/content/hugging_face/hugging-face/" | python3 -c "import sys, json; print('✅ Content endpoint working') if json.load(sys.stdin) else print('❌ Failed')"

echo "4. Testing Hugging Face Repositories endpoint..."
curl -s -u "$AUTH" "$BASE_URL/pulp/api/v3/repositories/hugging_face/hugging-face/" | python3 -c "import sys, json; print('✅ Repositories endpoint working') if json.load(sys.stdin) else print('❌ Failed')"

echo "5. Testing Hugging Face Publications endpoint..."
curl -s -u "$AUTH" "$BASE_URL/pulp/api/v3/publications/hugging_face/hugging-face/" | python3 -c "import sys, json; print('✅ Publications endpoint working') if json.load(sys.stdin) else print('❌ Failed')"

echo
echo "=== All endpoint tests completed ==="
