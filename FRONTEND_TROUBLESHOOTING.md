# Frontend Troubleshooting

## Your App URLs

- **Frontend:** https://nimble-granite-478311-u2.web.app
- **Backend API:** https://eu-legislation-api-428461461446.europe-west1.run.app

## Status: ✅ Everything is Configured Correctly

I tested the backend API and it's working perfectly:
- CORS is configured for your Firebase domain
- API returns data successfully
- The frontend build includes the correct backend URL

## How to Check if It's Working

### 1. Open Your Frontend
Go to: https://nimble-granite-478311-u2.web.app

### 2. Open Browser Console
- Press `F12` (or right-click → Inspect)
- Click the "Console" tab

### 3. Check for Errors
Look for any red error messages. Common issues:

**If you see "CORS error":**
- The backend CORS is already configured correctly
- Try a hard refresh: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)

**If you see "Failed to fetch" or "Network error":**
- Check if the backend is still running
- Test backend directly: https://eu-legislation-api-428461461446.europe-west1.run.app/

**If you see "404 Not Found":**
- The API endpoint might be wrong
- Check the Network tab to see what URL it's trying to call

### 4. Test Backend Directly

Open this URL in your browser:
https://eu-legislation-api-428461461446.europe-west1.run.app/

You should see:
```json
{"status":"ok","service":"EU Legislation RAG API","version":"1.0.0"}
```

### 5. Check Network Tab

In browser dev tools:
1. Click "Network" tab
2. Try using the app (select a category)
3. Look for requests to `eu-legislation-api-428461461446.europe-west1.run.app`
4. Click on any failed requests to see the error

## Common Solutions

### Hard Refresh the Frontend
The browser might be caching the old version:
- Windows: `Ctrl + Shift + R`
- Mac: `Cmd + Shift + R`

### Clear Browser Cache
1. Open Dev Tools (F12)
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload"

### Check if Backend is Sleeping
Cloud Run services can "sleep" after inactivity. First request wakes it up (takes 10-30 seconds).

Try accessing the backend URL directly first, then use the frontend.

## What to Send Me

If it's still not working, send me:

1. **Console errors** (screenshot of red errors in Console tab)
2. **Network errors** (screenshot of failed requests in Network tab)
3. **What happens** when you try to use the app

## Quick Test

Run this in your browser console (F12 → Console tab) while on your frontend:

```javascript
fetch('https://eu-legislation-api-428461461446.europe-west1.run.app/')
  .then(r => r.json())
  .then(d => console.log('Backend working:', d))
  .catch(e => console.error('Backend error:', e))
```

Should print: `Backend working: {status: "ok", ...}`
