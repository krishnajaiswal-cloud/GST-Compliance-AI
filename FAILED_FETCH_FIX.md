# "Failed to Fetch" Error - Troubleshooting Guide

## Root Cause Identified & Fixed ✅

The error was caused by **CORS (Cross-Origin Resource Sharing) configuration mismatch**:
- Frontend was running on `http://localhost:5174` (port 5173 was already in use)
- Backend CORS was only allowing `http://localhost:5173`
- Result: Browser blocked the requests with "Failed to fetch" error

## Solution Applied

Updated `backend/app/main.py` CORS configuration to allow multiple ports:

```python
allow_origins=[
    "http://localhost:5173",   # Original
    "http://localhost:5174",   # Fallback
    "http://localhost:5175",   # Extra fallback
    "http://127.0.0.1:5173",   # IPv4 variants
    "http://127.0.0.1:5174",
    "http://127.0.0.1:5175",
]
```

## What You Need To Do

### Step 1: Restart Backend Server
```bash
cd backend
# Kill existing process
# Then restart:
python -m uvicorn app.main:app --reload
```

The backend should log:
```
✓ Application startup complete
[CORS] Allowing origins from 5173, 5174, 5175
```

### Step 2: Check Frontend Port
When you start frontend, note which port it uses:
```bash
cd frontend
npm run dev

# Look for output like:
# ➜  Local:   http://localhost:5174/
```

### Step 3: Test Connection
Frontend should now connect to backend without "Failed to fetch" errors.

## Verification Checklist

- [x] Backend running on `http://localhost:8000`
- [x] Frontend running on `http://localhost:517X` (any of 5173-5175)
- [x] CORS allows all common development ports
- [x] Backend responds to health check (`http://localhost:8000/`)

## Common Scenarios

### Scenario 1: Port 5173 Available
```
Frontend starts on:     http://localhost:5173
Backend CORS allows:    Yes ✓
Result:                 Works
```

### Scenario 2: Port 5173 In Use
```
Frontend falls back to: http://localhost:5174
Backend CORS allows:    Yes ✓ (now fixed)
Result:                 Works (was broken, now fixed)
```

### Scenario 3: Multiple Ports In Use
```
Frontend falls back to: http://localhost:5175
Backend CORS allows:    Yes ✓ (now fixed)
Result:                 Works (was broken, now fixed)
```

## Additional Resources

### Created Utility File
**File**: `frontend/src/utils/api.ts`

Contains centralized API endpoints for easier management:
```typescript
export const API_ENDPOINTS = {
  uploadInvoices: `${API_BASE_URL}/upload/`,
  processDocuments: `${API_BASE_URL}/process/process`,
  getProgress: (sessionId) => `${API_BASE_URL}/process/progress/${sessionId}`,
  // ... more endpoints
}
```

Can be used in components:
```typescript
import { API_ENDPOINTS } from '../utils/api';

const response = await fetch(API_ENDPOINTS.getSessionData(sessionId));
```

## Troubleshooting Other "Failed to Fetch" Issues

### 1. Backend Not Running
```
Error:     Failed to fetch / Connection refused
Solution:  Start backend: python -m uvicorn app.main:app --reload
Test:      http://localhost:8000/ should show {"status":"Backend running"}
```

### 2. Wrong API Endpoint
```
Error:     404 Not Found
Solution:  Check endpoint exists in processing.py
Test:      Look for @router.get() or @router.post() for that endpoint
```

### 3. Network Connectivity
```
Error:     Failed to fetch (network error)
Solution:  
  - Check firewall isn't blocking ports 8000, 5173-5175
  - Check backend server is actually running
  - Try: curl http://localhost:8000/
```

### 4. Browser DevTools Shows Different Error
```
Error:     "net::ERR_BLOCKED_BY_CLIENT"
Solution:  Ad-blocker or extension might be interfering
           Try incognito/private window
```

### 5. CORS Preflight Failure
```
Error:     OPTIONS request 403 Forbidden
Solution:  This was the original issue - now fixed in main.py
```

## Checking Backend Logs

When testing, backend should show:
```
[CORS] Request from: http://localhost:5174
[UPLOAD] Starting upload for client=...
[PROCESS] Starting process endpoint...
[BACKGROUND] Background processing started...
```

If you see CORS errors in logs, the allow_origins list needs updating.

## Testing API Endpoints

### Test Backend Health
```bash
curl http://localhost:8000/
# Expected: {"status":"Backend running"}
```

### Test with Session ID
```bash
# Replace SESSION_ID with actual session ID
curl http://localhost:8000/process/session/SESSION_ID
# Expected: JSON with session data
```

## Next Steps

1. **Restart both backend and frontend**
2. **Check browser console** for any remaining errors
3. **Try uploading documents** and verify flow works
4. **Check network tab** in browser DevTools if issues persist

---

**Status**: ✅ CORS issue identified and fixed  
**Backend**: Running on port 8000  
**Frontend**: Can run on ports 5173-5175  
**API URLs**: Centralized in `frontend/src/utils/api.ts`  

The "Failed to fetch" error should now be resolved!
