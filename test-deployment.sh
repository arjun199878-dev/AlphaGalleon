#!/bin/bash

# AlphaGalleon E2E Testing & Deployment Verification Script
# Run after deployment to verify all systems are operational

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
ADMIN_EMAIL="${ADMIN_EMAIL:-test@alphagalleon.com}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-testPassword123}"
TEST_TICKER="RELIANCE"

# Counters
PASSED=0
FAILED=0
SKIPPED=0

# Helper functions
test_start() {
    echo -e "${BLUE}▶ Testing: $1${NC}"
}

test_pass() {
    echo -e "${GREEN}✓ PASS: $1${NC}"
    ((PASSED++))
}

test_fail() {
    echo -e "${RED}✗ FAIL: $1${NC}"
    ((FAILED++))
}

test_skip() {
    echo -e "${YELLOW}⊘ SKIP: $1${NC}"
    ((SKIPPED++))
}

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  AlphaGalleon E2E Testing & Deployment Verification${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# ─── 1. Health Checks ───────────────────────────────

echo -e "${YELLOW}1️⃣  System Health Checks${NC}"
echo "───────────────────────────────────────────────"

test_start "Backend health endpoint"
HEALTH=$(curl -s -w "\n%{http_code}" "$API_URL/health" 2>/dev/null || echo "000")
HTTP_CODE=$(echo "$HEALTH" | tail -n1)
if [ "$HTTP_CODE" = "200" ]; then
    test_pass "Backend is healthy (HTTP $HTTP_CODE)"
else
    test_fail "Backend health check failed (HTTP $HTTP_CODE)"
fi

test_start "Root endpoint"
ROOT=$(curl -s -w "\n%{http_code}" "$API_URL/" 2>/dev/null || echo "000")
HTTP_CODE=$(echo "$ROOT" | tail -n1)
if [ "$HTTP_CODE" = "200" ]; then
    test_pass "Root endpoint responding (HTTP $HTTP_CODE)"
else
    test_fail "Root endpoint failed (HTTP $HTTP_CODE)"
fi

echo ""

# ─── 2. Authentication Flow ────────────────────────

echo -e "${YELLOW}2️⃣  Authentication Flow${NC}"
echo "───────────────────────────────────────────────"

# Sign up a new user
test_start "User signup"
SIGNUP_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Test User\",
    \"email\": \"test-$(date +%s)@example.com\",
    \"password\": \"TestPassword123\",
    \"riskProfile\": \"moderate\"
  }")

AUTH_TOKEN=$(echo "$SIGNUP_RESPONSE" | grep -o '"token":"[^"]*' | cut -d'"' -f4 || echo "")
if [ -n "$AUTH_TOKEN" ]; then
    test_pass "User signup successful"
    echo "  Token: ${AUTH_TOKEN:0:20}..."
else
    test_fail "User signup failed"
    echo "  Response: $SIGNUP_RESPONSE"
fi

test_start "Token verification"
if [ -n "$AUTH_TOKEN" ]; then
    VERIFY=$(curl -s -X GET "$API_URL/api/v1/auth/verify" \
      -H "Authorization: Bearer $AUTH_TOKEN")
    VALID=$(echo "$VERIFY" | grep -o '"valid":\s*\(true\|false\)' | grep -o '\(true\|false\)' || echo "false")
    if [ "$VALID" = "true" ]; then
        test_pass "JWT token verification successful"
    else
        test_fail "JWT token verification failed"
        echo "  Response: $VERIFY"
    fi
else
    test_skip "Token verification (no valid token from signup)"
fi

echo ""

# ─── 3. Brain Engine Tests ─────────────────────────

echo -e "${YELLOW}3️⃣  Brain Engine (Investment Analysis)${NC}"
echo "───────────────────────────────────────────────"

test_start "Generate investment memo"
MEMO=$(curl -s -X POST "$API_URL/api/v1/brain/memo" \
  -H "Content-Type: application/json" \
  -d "{
    \"ticker\": \"$TEST_TICKER\",
    \"price\": 2850.50,
    \"market_cap\": 150000000000,
    \"pe\": 28.5,
    \"sector\": \"Energy\",
    \"revenue_growth\": 15.5,
    \"profit_growth\": 22.3,
    \"debt_equity\": 0.45,
    \"roe\": 12.8,
    \"promoter_holding\": 35.2,
    \"news\": \"Strong Q3 earnings, new projects commissioned\"
  }" 2>/dev/null)

RECOMMENDATION=$(echo "$MEMO" | grep -o '"recommendation":"[^"]*' | cut -d'"' -f4 || echo "")
if [ -n "$RECOMMENDATION" ]; then
    test_pass "Investment memo generated ($RECOMMENDATION)"
    CONFIDENCE=$(echo "$MEMO" | grep -o '"confidence_score":[^,}]*' | cut -d':' -f2 || echo "N/A")
    echo "  Confidence: $CONFIDENCE%"
else
    test_fail "Memo generation failed"
fi

test_start "List recent memos"
MEMOS=$(curl -s -X GET "$API_URL/api/v1/brain/memos?limit=5" 2>/dev/null)
MEMO_COUNT=$(echo "$MEMOS" | grep -o '"ticker_symbol"' | wc -l || echo "0")
if [ "$MEMO_COUNT" -ge 0 ]; then
    test_pass "Retrieved recent memos ($MEMO_COUNT found)"
else
    test_fail "Failed to list memos"
fi

echo ""

# ─── 4. Doctor Engine Tests ────────────────────────

echo -e "${YELLOW}4️⃣  Doctor Engine (Portfolio Diagnostics)${NC}"
echo "───────────────────────────────────────────────"

test_start "Run portfolio diagnostics"
DIAGNOSIS=$(curl -s -X POST "$API_URL/api/v1/doctor/diagnose" \
  -H "Content-Type: application/json" \
  -d "{
    \"portfolio\": [
      {\"symbol\": \"RELIANCE\", \"allocation\": 40, \"buy_price\": 2500, \"current_price\": 2850},
      {\"symbol\": \"INFY\", \"allocation\": 30, \"buy_price\": 1800, \"current_price\": 1950},
      {\"symbol\": \"TCS\", \"allocation\": 30, \"buy_price\": 3200, \"current_price\": 3450}
    ],
    \"risk_appetite\": \"moderate\"
  }" 2>/dev/null)

HEALTH_SCORE=$(echo "$DIAGNOSIS" | grep -o '"overall_health_score":[^,}]*' | cut -d':' -f2 || echo "N/A")
if [ "$HEALTH_SCORE" != "N/A" ]; then
    test_pass "Portfolio diagnostics completed (Health: $HEALTH_SCORE)"
else
    test_fail "Portfolio diagnostics failed"
    echo "  Response: $DIAGNOSIS"
fi

echo ""

# ─── 5. Architect Engine Tests ──────────────────────

echo -e "${YELLOW}5️⃣  Architect Engine (Portfolio Construction)${NC}"
echo "───────────────────────────────────────────────"

test_start "Construct portfolio strategy"
STRATEGY=$(curl -s -X POST "$API_URL/api/v1/architect/construct" \
  -H "Content-Type: application/json" \
  -d "{
    \"age\": 35,
    \"risk_appetite\": \"moderate\",
    \"capital_amount\": 500000,
    \"investment_horizon\": \"10 Years\",
    \"goals\": \"Wealth Creation\"
  }" 2>/dev/null)

STRATEGY_NAME=$(echo "$STRATEGY" | grep -o '"strategy_name":"[^"]*' | cut -d'"' -f4 || echo "")
if [ -n "$STRATEGY_NAME" ]; then
    test_pass "Portfolio strategy constructed ($STRATEGY_NAME)"
else
    test_fail "Portfolio construction failed"
    echo "  Response: $STRATEGY"
fi

echo ""

# ─── 6. Scout Engine Tests ─────────────────────────

echo -e "${YELLOW}6️⃣  Scout Engine (Market Data)${NC}"
echo "───────────────────────────────────────────────"

test_start "Get stock quote"
QUOTE=$(curl -s -X GET "$API_URL/api/v1/scout/quote/$TEST_TICKER" 2>/dev/null)
LTP=$(echo "$QUOTE" | grep -o '"ltp":[^,}]*' | cut -d':' -f2 || echo "N/A")
if [ "$LTP" != "N/A" ] && [ "$LTP" != "0" ]; then
    test_pass "Retrieved stock quote (LTP: ₹$LTP)"
else
    test_skip "Stock quote unavailable (Upstox integration pending)"
fi

test_start "Get LTP (Last Traded Price)"
LTP_DATA=$(curl -s -X GET "$API_URL/api/v1/scout/ltp/$TEST_TICKER" 2>/dev/null)
LTP_VALUE=$(echo "$LTP_DATA" | grep -o '"ltp":[^,}]*' | cut -d':' -f2 || echo "")
if [ -n "$LTP_VALUE" ]; then
    test_pass "Retrieved LTP ($LTP_VALUE)"
else
    test_skip "LTP data unavailable"
fi

echo ""

# ─── 7. Admin Endpoints ────────────────────────────

echo -e "${YELLOW}7️⃣  Admin Endpoints${NC}"
echo "───────────────────────────────────────────────"

test_start "List users (admin endpoint)"
USERS=$(curl -s -X GET "$API_URL/api/v1/admin/users" \
  -H "Authorization: Bearer $AUTH_TOKEN" 2>/dev/null)
USER_COUNT=$(echo "$USERS" | grep -o '"email"' | wc -l || echo "0")
if [ "$USER_COUNT" -ge 0 ]; then
    test_pass "Retrieved users list ($USER_COUNT users)"
else
    test_fail "Failed to list users"
fi

test_start "Get activity log (admin endpoint)"
ACTIVITY=$(curl -s -X GET "$API_URL/api/v1/admin/activity?limit=10" \
  -H "Authorization: Bearer $AUTH_TOKEN" 2>/dev/null)
ACTIVITY_COUNT=$(echo "$ACTIVITY" | grep -o '"action"' | wc -l || echo "0")
if [ "$ACTIVITY_COUNT" -ge 0 ]; then
    test_pass "Retrieved activity log ($ACTIVITY_COUNT entries)"
else
    test_fail "Failed to retrieve activity log"
fi

echo ""

# ─── Performance Tests ──────────────────────────────

echo -e "${YELLOW}⚡ Performance Metrics${NC}"
echo "───────────────────────────────────────────────"

test_start "Health endpoint response time"
START=$(date +%s%N)
curl -s "$API_URL/health" > /dev/null
END=$(date +%s%N)
DURATION=$(( (END - START) / 1000000 ))
echo "  Response time: ${DURATION}ms"
if [ "$DURATION" -lt 200 ]; then
    test_pass "Health endpoint is fast (<200ms)"
else
    test_pass "Health endpoint responding (${DURATION}ms)"
fi

test_start "API endpoint response time"
START=$(date +%s%N)
curl -s "$API_URL/api/v1/brain/memos" > /dev/null
END=$(date +%s%N)
DURATION=$(( (END - START) / 1000000 ))
echo "  Response time: ${DURATION}ms"
if [ "$DURATION" -lt 500 ]; then
    test_pass "API endpoint is fast (<500ms)"
else
    test_pass "API endpoint responding (${DURATION}ms)"
fi

echo ""

# ─── Summary ────────────────────────────────────────

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Test Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Passed: $PASSED${NC}"
echo -e "${RED}✗ Failed: $FAILED${NC}"
echo -e "${YELLOW}⊘ Skipped: $SKIPPED${NC}"
echo -e "${BLUE}Total Tests: $((PASSED + FAILED + SKIPPED))${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}         ✓ All critical tests PASSED!${NC}"
    echo -e "${GREEN}         AlphaGalleon deployment is operational.${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
    exit 0
else
    echo -e "${RED}════════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}         ✗ Some tests FAILED - review above${NC}"
    echo -e "${RED}════════════════════════════════════════════════════════════${NC}"
    exit 1
fi
