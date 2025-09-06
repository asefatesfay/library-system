#!/bin/bash

# Google Cloud Run Deployment Script for Library System Frontend
# Make sure you're logged in: gcloud auth login
# Set your project: gcloud config set project YOUR_PROJECT_ID

set -e

# Configuration
PROJECT_ID="your-project-id"  # Replace with your actual project ID
REGION="us-central1"          # Use us-central1 for free tier
SERVICE_NAME="library-frontend"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 Deploying Library System Frontend to Google Cloud Run${NC}"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if logged in
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${RED}❌ Not logged in to gcloud. Please run: gcloud auth login${NC}"
    exit 1
fi

# Get current project
CURRENT_PROJECT=$(gcloud config get-value project)
if [ -z "$CURRENT_PROJECT" ]; then
    echo -e "${RED}❌ No project set. Please run: gcloud config set project YOUR_PROJECT_ID${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Current project: ${CURRENT_PROJECT}${NC}"

# Build the Docker image
echo -e "${YELLOW}📦 Building Docker image...${NC}"
docker build -f Dockerfile.prod -t ${IMAGE_NAME}:latest .

# Push to Google Container Registry
echo -e "${YELLOW}📤 Pushing image to Google Container Registry...${NC}"
docker push ${IMAGE_NAME}:latest

# Deploy to Cloud Run
echo -e "${YELLOW}🚀 Deploying to Cloud Run...${NC}"
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME}:latest \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --set-env-vars="NEXT_PUBLIC_API_URL=https://your-backend-url" \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=10 \
  --concurrency=80 \
  --timeout=300

echo -e "${GREEN}🎉 Frontend deployed successfully!${NC}"
echo -e "${GREEN}📱 Your app is available at: $(gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format='value(status.url)')${NC}"

# Optional: Set up custom domain (requires manual DNS setup)
echo -e "${YELLOW}💡 To set up a custom domain:${NC}"
echo "1. gcloud run domain-mappings create --service=${SERVICE_NAME} --domain=yourdomain.com --region=${REGION}"
echo "2. Configure DNS to point to the provided CNAME"
