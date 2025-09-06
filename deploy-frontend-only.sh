#!/bin/bash

# Simple deployment script for frontend only
# Usage: ./deploy-frontend-only.sh [your-project-id] [backend-url]

set -e

PROJECT_ID=${1:-"your-project-id"}
BACKEND_URL=${2:-"https://your-backend-url"}
REGION="us-west1"
SERVICE_NAME="library-system-frontend"

echo "🚀 Deploying Frontend to Google Cloud Run"
echo "📋 Project: $PROJECT_ID"
echo "🔗 Backend URL: $BACKEND_URL"

# Navigate to frontend directory
cd frontend

# Build and deploy in one step using Cloud Build
gcloud builds submit \
  --tag gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --config cloudbuild.yaml

# Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars="NEXT_PUBLIC_API_URL=$BACKEND_URL" \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=10 \
  --concurrency=80 \
  --timeout=300

# Get the deployed URL
FRONTEND_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')

echo "✅ Deployment complete!"
echo "🌐 Frontend URL: $FRONTEND_URL"
