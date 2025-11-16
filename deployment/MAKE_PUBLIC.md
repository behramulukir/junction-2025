# Make Backend Publicly Accessible

Your backend is deployed but needs to be made public. Do ONE of these:

## Option 1: Cloud Console (Easiest - 30 seconds)

1. Go to: https://console.cloud.google.com/run?project=nimble-granite-478311-u2
2. Click on `eu-legislation-api`
3. Click "SECURITY" tab
4. Click "ALLOW UNAUTHENTICATED INVOCATIONS"
5. Click "SAVE"

## Option 2: Command Line

Ask someone with Owner/Editor role to run:
```bash
gcloud run services add-iam-policy-binding eu-legislation-api --region=europe-west1 --member=allUsers --role=roles/run.invoker --project=nimble-granite-478311-u2
```

## Test It Works

After making it public, test:
```bash
curl https://eu-legislation-api-428461461446.europe-west1.run.app/
```

Should return:
```json
{"status":"ok","service":"EU Legislation RAG API","version":"1.0.0"}
```

Then continue with frontend deployment!
