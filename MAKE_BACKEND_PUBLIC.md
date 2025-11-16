# Make Backend Publicly Accessible

Your backend is deployed at:
**https://eu-legislation-api-428461461446.europe-west1.run.app**

It just needs to be made public so your frontend can access it.

---

## Step-by-Step Instructions (30 seconds)

### 1. Open Cloud Run Console

Click this link (opens in your browser):
👉 **https://console.cloud.google.com/run?project=nimble-granite-478311-u2**

### 2. Find Your Service

You'll see a list of Cloud Run services. Look for:
- **eu-legislation-api** 

Click on it.

### 3. Go to Security Tab

At the top of the page, you'll see tabs:
- DETAILS
- METRICS  
- LOGS
- **SECURITY** ← Click this one
- YAML

### 4. Allow Public Access

You'll see a section called "Authentication"

Current setting: **Require authentication** ❌

Click the **"ALLOW UNAUTHENTICATED INVOCATIONS"** button

A dialog will pop up asking you to confirm. Click **"SAVE"** or **"ALLOW"**

### 5. Verify It Works

Open a new browser tab and go to:
**https://eu-legislation-api-428461461446.europe-west1.run.app/**

You should see:
```json
{
  "status": "ok",
  "service": "EU Legislation RAG API",
  "version": "1.0.0"
}
```

✅ **Done!** Your backend is now publicly accessible.

---

## Visual Guide

Here's what you're looking for:

```
Cloud Run Console
├── Services list
│   └── eu-legislation-api ← Click here
│
└── Service details page
    ├── DETAILS tab
    ├── METRICS tab
    ├── LOGS tab
    ├── SECURITY tab ← Click here
    │   └── Authentication section
    │       └── [ALLOW UNAUTHENTICATED INVOCATIONS] ← Click this button
    └── YAML tab
```

---

## Troubleshooting

**"I don't have permission to change this"**
- You need to be an Owner or Editor on the project
- Ask whoever created the GCP project to give you the "Cloud Run Admin" role
- Or ask them to make this change for you

**"I can't find the SECURITY tab"**
- Make sure you clicked on the service name (eu-legislation-api)
- You should be on the service details page, not the services list

**"The page shows an error after I make it public"**
- That's okay! As long as it's not a "Forbidden" error
- Check the Cloud Run logs to see what's happening
- The service might be starting up (takes 10-30 seconds on first request)

**"I see 'Service Unavailable'"**
- The container might be starting up - wait 30 seconds and refresh
- Check logs: Click "LOGS" tab to see what's happening

---

## Alternative: Command Line (if you have permissions)

If you prefer using the command line:

```bash
gcloud run services add-iam-policy-binding eu-legislation-api \
  --region=europe-west1 \
  --member=allUsers \
  --role=roles/run.invoker \
  --project=nimble-granite-478311-u2
```

---

## Next Step

Once the backend is public and working, you can deploy the frontend!

See `DEPLOYMENT_STATUS.md` for frontend deployment instructions.
