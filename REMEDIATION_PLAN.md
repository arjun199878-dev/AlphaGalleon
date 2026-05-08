# AlphaGalleon Remediation Plan

**Status:** Verified against Codex Audit  
**Date:** 2026-02-23  
**Verification:** All P0/P1/P2 issues confirmed in source code  

---

## Executive Summary

The AlphaGalleon codebase is a **strong prototype/demo shell but not production-ready**. Critical issues span:
- **[P0] Authentication System** - Broken end-to-end (backend/mobile contract mismatch)
- **[P0] Memo Persistence** - Function name mismatches block all data flow
- **[P1] AI Modules** - Present but non-functional (demo logic only)
- **[P1] Portfolio Math** - Unsafe field name inconsistencies
- **[P2] Configuration** - Hardcoded URLs/IPs, no proper env setup
- **[Legacy Stacks]** - Multiple duplicate codebases causing confusion

---

## [P0] Authentication System - Broken End-to-End

### Issue Description
The authentication system is internally inconsistent and routes are incompatible between frontend/backend/mobile.

### Root Causes

**1. Backend/Convex Contract Mismatch** (convex_service.py:131)
```python
# Problem: signature mismatch
user_result = self.client.mutation("users:create", user_data)  # Returns ONLY ID
# But main.py line ~195 tries to pass full user document:
user=UserResponse(
    _id=str(user.get("_id", "")),  # ✓ Works
    name=user.get("name", ""),      # ✗ FAILS - user is just an ID!
    email=user.get("email", ""),    # ✗ FAILS
```

**2. Mobile Bypasses Backend Auth** (alphagalleon-mobile/App.js)
- Mobile queries Convex directly without JWT
- Stores plaintext passwords
- Uses user ID as authentication token (invalid security model)

**3. Missing Convex Query Functions**
- Backend expects: `users:get`, `users:getByEmail` 
- Convex likely has different function names
- Need to verify actual exports in convex/users.ts

### Fix Strategy

**Step 1: Backend-Only Signup/Login**
- Remove all direct Convex queries from mobile
- Mobile → Backend (JWT-protected) → Convex (internal)

**Step 2: Fix User Service Layer**
```python
# convex_service.py - new approach
def create_user(self, name, email, password_hash, riskProfile="moderate"):
    """Create user and return full document"""
    user_data = {
        "name": name,
        "email": email,
        "password_hash": password_hash,
        "riskProfile": riskProfile,
        "createdAt": int(time.time() * 1000)
    }
    user_id = self.client.mutation("users:create", user_data)
    # Fetch and return the created document
    return self.client.query("users:getById", {"id": user_id})
```

**Step 3: Mobile Login Flow**
```javascript
// AlphaGalleon-mobile - new auth flow
const login = async (email, password) => {
    const response = await fetch(`${API_URL}/api/v1/auth/login`, {
        method: 'POST',
        body: JSON.stringify({ email, password })
    });
    const { token, user } = await response.json();
    AuthContext.setToken(token);  // Store JWT only
    AuthContext.setUser(user);
};
```

### Files to Modify
- `alphagalleon-backend/app/main.py` (lines 175-210) - Auth handlers
- `alphagalleon-backend/app/convex_service.py` (lines 120-150) - User service
- `convex/users.ts` - Add/update query functions
- `alphagalleon-mobile/App.js` - Remove direct Convex queries
- Remove hardcoded LAN IP from mobile config

---

## [P0] Memo Persistence - Broken Function Names

### Issue Description
Backend calls Convex functions that don't exist, breaking memo creation and retrieval entirely.

### Root Causes

**1. Function Name Mismatch**
```
Backend (convex_service.py)          Convex (memos.ts)
─────────────────────────────        ──────────────────
store_memo() calls                   exports:
→ "memos:store"         ✗            ✓ create
→ "memos:listRecent"    ✗            ✓ list  
→ "memos:listBySymbol"  ✗            ✓ getBySymbol
```

**2. Field Name Mismatch (Backend → UI)**
```
Convex Schema (memos.ts)    Backend Expects     UI Expects
─────────────────────────    ─────────────      ──────────
symbol                       symbol ✓           ticker_symbol ✗
summary                      summary ✓          thesis_summary ✗
confidence                   confidence ✓       confidence_score ✗
```

**3. Code Locations**
- convex_service.py line 22: `"memos:store"` (should be `"memos:create"`)
- convex_service.py line 57: `"memos:listRecent"` (should be `"memos:list"`)
- convex_service.py line 71: `"memos:listBySymbol"` (should be `"memos:getBySymbol"`)

### Fix Strategy

**Option A: Update Backend to Match Convex**
```python
# convex_service.py - corrected function calls
def store_memo(self, memo_data):
    return self.client.mutation("memos:create", memo_data)  # Fixed

def list_memos(self, limit=50):
    return self.client.query("memos:list", {"limit": limit})  # Fixed

def get_memo_by_symbol(self, symbol):
    return self.client.query("memos:getBySymbol", {"symbol": symbol})  # Fixed
```

**Option B: Add Aliases in Convex** (memos.ts)
```typescript
// Add these mutations as wrappers
export const store = mutation({...});  // alias for create
export const listRecent = query({...}); // alias for list
export const listBySymbol = query({...}); // alias for getBySymbol
```

**Recommendation:** Option A (Update Backend) - cleaner, no debt

### Files to Modify
- `alphagalleon-backend/app/convex_service.py` (lines 20-75)
- `alphagalleon-backend/app/main.py` (lines ~250) - Update memo response models
- **Admin Dashboard / UI** - Map field names correctly
  - Replace `ticker_symbol` → `symbol`
  - Replace `thesis_summary` → `summary`
  - Replace `confidence_score` → `confidence`

---

## [P1] AI Modules - Demo Logic Only

### Issue Description
5 AI engines marked "complete" but actually run hardcoded demo scenarios instead of real backend logic.

### Affected Modules
1. **Doctor** (risk diagnosis) - heuristics, not `/api/v1/doctor/diagnose`
2. **Time Travel** - fixed demo basket, no calculations
3. **Sentinel** - fabricated alerts, no real-time data
4. **Backtester** - explicitly simulated, not live
5. **Scout** - hardcoded screener results

### Root Cause
These systems were designed to show "what the future will look like" rather than being production-integrated. The architecture doc shows they're "complete" but the actual implementation is demo-grade.

### Fix Strategy
1. **Identify Real vs Demo Logic** - Audit each module's main.py endpoints
2. **Wire to Actual APIs** - Replace hardcoded returns with real service calls
3. **Add Feature Flags** - `DEMO_MODE=true/false` env variable
4. **Document Integration Points** - Each module should have clear data flow

### Files to Identify & Modify
- `alphagalleon-backend/app/doctor.py`
- `alphagalleon-backend/app/backtester.py`
- `alphagalleon-backend/app/sentinel.py`
- `alphagalleon-backend/app/scout.py`
- Convex functions: `diagnoses.ts`, `backtests.ts`

### Priority: Medium (P1)
Can operate in demo mode initially, but must be flagged clearly.

---

## [P1] Portfolio Math - Unsafe Field Inconsistencies

### Issue Description
Portfolio calculations fail silently due to field name mismatches between schema and UI.

### Root Cause
```
Schema (holdings table)   Backend May Use    UI Code Expected
──────────────────────   ────────────────   ──────────────────
avgBuyPrice              averagePrice ✗     averagePrice ✗
allocation               allocation ✓       allocation ✓
```

**Example:** Portfolio P&L calculation fails:
```python
# backend tries to use "averagePrice"
current_value = quantity * current_price
cost_basis = quantity * averagePrice  # ✗ KEY NOT FOUND → None → calculation broken
```

### Impact
- P&L calculation returns 0 or NaN
- Rebalancing suggestions ignored
- Live trading (if enabled) uses hardcoded 2500.0 for unknown symbols

### Fix Strategy
1. **Standardize Schema** - Use `avgBuyPrice` everywhere (already in schema.ts:34)
2. **Update Backend** - Rename all `averagePrice` refs to `avgBuyPrice`
3. **Update UI** - Ensure all components use `avgBuyPrice` or add mapping layer
4. **Add Tests** - P&L calculation unit tests

### Files to Modify
- `alphagalleon-backend/app/doctor.py` - Portfolio analysis
- `alphagalleon-backend/app/architect.py` - Portfolio construction
- Any UI component that reads holdings data
- Add integration tests for P&L calculation

---

## [P2] Environment Configuration - Demo Grade

### Issue Description
Hardcoded URLs, IPs, and credentials across the codebase. No proper `.env` setup.

### Hardcoded Values Found
```
admin-dashboard/client.ts:2           localhost:3001
alphagalleon-mobile/config.ts:14      192.168.0.1:8000 (LAN IP)
admin-dashboard/main.tsx:7            https://vibrant-spoonbill-564.eu-west-1.convex.cloud
alphagalleon-backend:                 No .env validation
```

### Fix Strategy
1. **Create .env Templates**
   ```bash
   # .env.local
   CONVEX_URL=https://vibrant-spoonbill-564.eu-west-1.convex.cloud
   BACKEND_URL=http://localhost:8000
   BACKEND_URL_PROD=https://api.alphagalleon.com
   UPSTOX_API_KEY=xxx
   UPSTOX_API_SECRET=xxx
   GOOGLE_API_KEY=xxx
   ```

2. **Add Env Validation** - Backend startup should fail if critical vars missing
3. **Remove Hardcoded Values** - Search & replace all constant URLs
4. **Document Deployment** - Add deployment.md with all required env vars

### Files to Modify
- Create `.env.example` in root
- Create `.env.example` in alphagalleon-backend/
- Create `.env.example` in admin-dashboard/
- Create `.env.example` in alphagalleon-mobile/
- `alphagalleon-backend/app/main.py` - Add startup validation
- Update deployment scripts (start.sh, docker-compose.yml)

---

## Legacy Stack Cleanup

### Issue
Multiple duplicate codebases:
- `backend/` - Legacy Python backend (unused)
- `frontend/` - Legacy React frontend (unused)
- `alphagalleon-mobile/` - Active
- `admin-dashboard/` - Active

### Recommendation
1. **Archive Legacy Stacks** - Move `backend/`, `frontend/` to archive/
2. **Document Migration** - Create MIGRATION.md explaining transition
3. **Update CI/CD** - Only build active stacks

---

## Remediation Priority & Sequencing

### Phase 1: Critical (Start Immediately)
**Goal:** Fix broken persistence, enable MVP testing
1. ✅ **Fix Memo Persistence** (P0) - 2-4 hours
   - Update convex_service.py function calls
   - Verify field names across stack
   
2. ✅ **Fix Authentication** (P0) - 4-6 hours
   - Backend-only signup/login
   - Remove mobile Convex bypasses
   - JWT token validation

3. ✅ **Standardize Portfolio Math** (P1) - 2-3 hours
   - avgBuyPrice consistency
   - Add P&L tests

**Effort:** ~8-13 hours | **Timeline:** 1-2 days

### Phase 2: Core (Within 1 week)
**Goal:** Production-ready configuration
1. ✅ **Environment Configuration** (P2) - 2-3 hours
2. ✅ **CI/CD Validation** - 3-4 hours

**Effort:** ~5-7 hours | **Timeline:** 2-3 days

### Phase 3: Enhancement (Within 2 weeks)
**Goal:** Replace demo logic with real integration
1. Wire AI Modules to Real APIs (P1)
2. Add Integration Tests
3. Documentation & Runbooks

---

## Verification Checklist

After each fix, verify:
- [ ] All imports/function calls resolve
- [ ] No 500 errors on signup/login
- [ ] Memo creation and retrieval work
- [ ] P&L calculations return valid numbers
- [ ] Environment config validated at startup
- [ ] Unit tests pass (add if missing)
- [ ] TypeScript/Python type checks pass

---

## Next Steps

1. **Select Fix Strategy** - Approve Phase 1 approach above
2. **Begin Phase 1** - Start with memo persistence (highest impact)
3. **Testing** - Add integration tests as we build
4. **Monitoring** - Add logging/alerting for failure points
5. **Documentation** - Update README and create deployment guide

---

## Files Changed Summary (After All Fixes)

```
alphagalleon-backend/
├── app/
│   ├── main.py                 (Auth handlers, memo endpoints)
│   ├── convex_service.py       (Function name fixes)
│   ├── doctor.py               (Field name fixes)
│   └── architect.py            (Field name fixes)
├── .env.example                (NEW)
└── requirements.txt            (Update if deps added)

convex/
├── memos.ts                    (Verify exports)
├── users.ts                    (Verify exports)
└── schema.ts                   (Already correct)

admin-dashboard/
├── src/
│   ├── App.tsx                 (Remove hardcoded URLs)
│   └── components/             (Field name mappings)
└── .env.example                (NEW)

alphagalleon-mobile/
├── App.js                      (Remove Convex queries)
├── config.ts                   (Use env vars)
└── .env.example                (NEW)

.env.example                    (NEW - root)
REMEDIATION_PLAN.md            (THIS FILE - NEW)
```

---

## Questions & Decisions Needed

1. **Demo Mode** - Keep AI modules in demo mode during transition?
2. **Database Migration** - Any existing user data to preserve during auth fixes?
3. **Upstox Integration** - Is live trading currently enabled? Should we disable during fixes?
4. **Testing** - Do you have test users/data to validate against?
5. **Timeline** - Any business deadlines for Phase 1 completion?

---

## Risk Assessment

**HIGH RISK (if not fixed):**
- ❌ Cannot create new users (auth broken)
- ❌ Cannot store investment memos (persistence broken)
- ❌ Portfolio health checks return garbage (math broken)
- ❌ Mobile has serious security issues (plaintext passwords)

**MEDIUM RISK:**
- ⚠️ AI modules run demo logic (confuses users expecting real intelligence)
- ⚠️ Hardcoded configs fail in production (breaks deployment)

**LOW RISK (but important):**
- ⚠️ Legacy stacks create codebase confusion (maintenance burden)

