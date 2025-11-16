# Quick Start - Deploy in 5 Minutes

## 1. One-Time Setup (2 minutes)

```bash
# Make scripts executable
chmod +x setup-deployment.sh deploy-backend.sh deploy-frontend.sh

# Run setup (enables APIs, configures project)
./setup-deployment.sh
```

This will:
- Verify you have gcloud and firebase CLI
- Enable required Google Cloud APIs
- Set your project to 428461461446
- Login to Firebase

## 2. Deploy Backend (2 minutes)

```bash
./deploy-backend.sh
```

**Save the URL it outputs!** You'll need it for the next step.

Example output:
```
✅ Deployment complete!
🌐 Your API is now live at:
https://eu-legislation-api-xxxxx-ew.a.run.app
```

## 3. Deploy Frontend (1 minute)

```bash
# Replace with YOUR backend URL from step 2
./deploy-frontend.sh https://eu-legislation-api-xxxxx-ew.a.run.app
```

## 4. Update CORS (30 seconds)

After frontend deploys, you'll get a Firebase URL like:
`https://428461461446.web.app`

Add it to `backend/api_server.py`:

```python
allow_origins=[
    "http://localhost:5173",
    "https://428461461446.web.app",  # Add this
    "https://428461461446.firebaseapp.com"  # And this
],
```

Then redeploy backend:
```bash
./deploy-backend.sh
```

## Done! 🎉

Your app is now live on the internet using your Google Cloud credits.

**View your app:**
- Frontend: https://428461461446.web.app
- Backend API: https://eu-legislation-api-xxxxx-ew.a.run.app
- API Docs: https://eu-legislation-api-xxxxx-ew.a.run.app/docs

## Troubleshooting

**"Permission denied" on scripts:**
```bash
chmod +x *.sh
```

**"gcloud not found":**
Install from: https://cloud.google.com/sdk/docs/install

**"firebase not found":**
```bash
npm install -g firebase-tools
```

**Backend fails to build:**
Check logs:
```bash
gcloud builds log --region=europe-west1
```

**Need help?**
See full guide: `DEPLOYMENT_GUIDE.md`
