# Library Management System - Deployment Guide

## Environment Variables

This application uses environment variables for sensitive configuration. Never commit secrets to your repository.

### Required Environment Variables

- `JWT_SECRET_KEY`: A secure secret key for JWT token signing

### Local Development Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Generate a secure JWT secret:
   ```bash
   python generate_secret.py
   ```

3. Copy the generated secret and add it to your `.env` file:
   ```bash
   JWT_SECRET_KEY=your-generated-secret-here
   ```

### GitHub Actions Deployment Setup

For deploying to GCP using GitHub Actions, you need to add the following secrets to your GitHub repository:

1. Go to your GitHub repository
2. Navigate to Settings → Secrets and variables → Actions
3. Add the following repository secrets:

#### Required GitHub Secrets

- `GCP_PROJECT_ID`: Your Google Cloud Project ID
- `GCP_SA_KEY`: Your Google Cloud Service Account JSON key
- `JWT_SECRET_KEY`: A secure JWT secret key (generate with `python generate_secret.py`)

#### Setting up GCP Service Account

1. Create a service account in your GCP project
2. Grant it the following roles:
   - Cloud Run Admin
   - Storage Admin
   - Cloud Build Editor
3. Create a JSON key for the service account
4. Copy the entire JSON content and add it as `GCP_SA_KEY` secret

#### Setting up JWT Secret

1. Run the secret generator:
   ```bash
   python generate_secret.py
   ```

2. Copy the generated secret key
3. Add it as `JWT_SECRET_KEY` in your GitHub repository secrets

### Manual GCP Deployment

If you prefer to deploy manually:

```bash
# Build and push the image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/library-system-api

# Deploy to Cloud Run with environment variables
gcloud run deploy library-system-api \
  --image gcr.io/YOUR_PROJECT_ID/library-system-api \
  --region us-west2 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars JWT_SECRET_KEY="your-secure-secret-here"
```

### Security Best Practices

1. **Never commit secrets to git**
2. **Use strong, randomly generated secrets**
3. **Rotate secrets periodically**
4. **Use different secrets for different environments**
5. **Monitor access to your secrets**

### Verification

After deployment, you can verify the environment variable is set correctly by checking the Cloud Run service configuration in the GCP Console.
