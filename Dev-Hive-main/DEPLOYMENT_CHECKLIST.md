# KTP Deployment Checklist for Render

## Pre-Deployment Checklist

- [ ] GitHub repository is pushed and up to date
- [ ] All required files are present:
  - [ ] `render.yaml`
  - [ ] `app.py`
  - [ ] `server/requirements.txt`
  - [ ] `frontend/streamlit_app.py`
  - [ ] `server/app.py` (Flask backend)

## API Keys Required

### Required Keys:
- [ ] **OpenAI API Key**
  - [ ] Go to [OpenAI Platform](https://platform.openai.com/api-keys)
  - [ ] Create new secret key
  - [ ] Copy the key

- [ ] **Pinecone API Key**
  - [ ] Go to [Pinecone Console](https://app.pinecone.io/)
  - [ ] Create new API key
  - [ ] Copy the key

- [ ] **Pinecone Index Name**
  - [ ] Create new index in Pinecone
  - [ ] Dimension: 1536
  - [ ] Metric: cosine
  - [ ] Copy the index name

### Optional Keys (for integrations):
- [ ] **GitHub Personal Access Token**
  - [ ] Go to [GitHub Settings > Tokens](https://github.com/settings/tokens)
  - [ ] Generate new token with `repo` scope
  - [ ] Copy the token

- [ ] **Notion Integration Token**
  - [ ] Go to [Notion Integrations](https://www.notion.so/my-integrations)
  - [ ] Create new integration
  - [ ] Copy the Internal Integration Token

- [ ] **Slack Bot Token**
  - [ ] Go to [Slack API Apps](https://api.slack.com/apps)
  - [ ] Create new app
  - [ ] Add bot token scopes: `channels:read`, `channels:history`, `users:read`
  - [ ] Install app to workspace
  - [ ] Copy the Bot User OAuth Token

## Render Deployment Steps

### Step 1: Create Render Account
- [ ] Go to [render.com](https://render.com)
- [ ] Sign up with GitHub
- [ ] Verify email address

### Step 2: Create Web Service
- [ ] Click "New +" → "Web Service"
- [ ] Connect GitHub account
- [ ] Select `ktp` repository
- [ ] Render will auto-detect `render.yaml`

### Step 3: Configure Environment Variables
In Render dashboard, add these environment variables:

```
OPENAI_API_KEY = your_openai_api_key_here
PINECONE_API_KEY = your_pinecone_api_key_here
PINECONE_INDEX_NAME = your_pinecone_index_name_here
GITHUB_TOKEN = your_github_token_here (optional)
NOTION_TOKEN = your_notion_token_here (optional)
SLACK_BOT_TOKEN = your_slack_token_here (optional)
FLASK_API_URL = http://localhost:5000
```

### Step 4: Deploy
- [ ] Click "Create Web Service"
- [ ] Wait for build to complete (5-10 minutes)
- [ ] Monitor build logs for errors

## Post-Deployment Verification

### Check Build Logs
- [ ] No error messages in build logs
- [ ] All dependencies installed successfully
- [ ] Both Flask and Streamlit started

### Test the Application
- [ ] Access the deployed URL
- [ ] Check if Streamlit interface loads
- [ ] Test token management in Integrations page
- [ ] Test basic functionality

### Common Issues & Solutions

#### Build Fails
- [ ] Check if all dependencies are in `server/requirements.txt`
- [ ] Verify Python version compatibility
- [ ] Check for syntax errors in code

#### Environment Variables Not Working
- [ ] Verify all required keys are set in Render dashboard
- [ ] Check key names match exactly (case-sensitive)
- [ ] Ensure keys are valid and have proper permissions

#### Application Not Starting
- [ ] Check if ports are correctly configured
- [ ] Verify `app.py` is the correct start command
- [ ] Check if both Flask and Streamlit can start

#### Pinecone Connection Issues
- [ ] Verify Pinecone index exists and is in correct region
- [ ] Check API key has access to the index
- [ ] Ensure index name matches exactly

## Deployment URL

Once deployed, your application will be available at:
```
https://your-app-name.onrender.com
```

## Support

If you encounter issues:
1. Check the build logs in Render dashboard
2. Verify all environment variables are set correctly
3. Test API keys individually
4. Check the application logs for runtime errors

## Security Notes

- [ ] Never commit API keys to Git
- [ ] Use environment variables in production
- [ ] Rotate API keys regularly
- [ ] Monitor usage and costs 