# KTP - Knowledge Transfer Platform Setup Guide

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ktp.git
   cd ktp
   ```

2. **Set up environment variables (Optional for local development)**
   ```bash
   # Option 1: For local development with .env file
   cp env.example server/.env
   nano server/.env  # or use your preferred editor
   
   # Option 2: Use the secure token management system (Recommended)
   # Just run the app and input tokens through the Streamlit interface
   ```

3. **Install dependencies**
   ```bash
   pip install -r server/requirements.txt
   ```

4. **Run the application**
   ```bash
   # For local development
   python run_ktp.py
   
   # Or for production deployment
   python app.py
   ```

5. **Access the application**
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:5000

## Required API Keys

### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Add it to `server/.env` as `OPENAI_API_KEY=your_key_here`

### Pinecone API Key
1. Go to [Pinecone Console](https://app.pinecone.io/)
2. Create a new API key
3. Create a new index (recommended: dimension=1536, metric=cosine)
4. Add both to `server/.env`:
   ```
   PINECONE_API_KEY=your_pinecone_api_key_here
   PINECONE_INDEX_NAME=your_index_name_here
   ```

### GitHub Personal Access Token
1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Generate a new token with `repo` scope
3. Add it to `server/.env` as `GITHUB_TOKEN=your_token_here`

### Notion Integration Token
1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Create a new integration
3. Copy the Internal Integration Token
4. Add it to `server/.env` as `NOTION_TOKEN=your_token_here`

### Slack Bot Token
1. Go to [Slack API Apps](https://api.slack.com/apps)
2. Create a new app
3. Add bot token scopes: `channels:read`, `channels:history`, `users:read`
4. Install the app to your workspace
5. Copy the Bot User OAuth Token
6. Add it to `server/.env` as `SLACK_BOT_TOKEN=your_token_here`

## Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for embeddings and Q&A | Yes |
| `PINECONE_API_KEY` | Pinecone API key for vector database | Yes |
| `PINECONE_INDEX_NAME` | Name of your Pinecone index | Yes |
| `GITHUB_TOKEN` | GitHub Personal Access Token | Optional |
| `NOTION_TOKEN` | Notion Integration Token | Optional |
| `SLACK_BOT_TOKEN` | Slack Bot User OAuth Token | Optional |
| `FLASK_ENV` | Flask environment (development/production) | No |
| `FLASK_DEBUG` | Enable Flask debug mode | No |
| `FLASK_API_URL` | Backend API URL | No |

## Security Notes

- **Never commit your `.env` file** - It's already in `.gitignore`
- **Use environment variables in production** - Don't rely on `.env` files
- **Rotate API keys regularly** - Especially if they're exposed
- **Use least privilege** - Only grant necessary permissions to API tokens

## Troubleshooting

### Common Issues

1. **"Module not found" errors**
   - Make sure you've installed all dependencies: `pip install -r server/requirements.txt`

2. **API key errors**
   - Verify your API keys are correct and have the right permissions
   - Check that the keys are properly formatted in the `.env` file

3. **Pinecone connection issues**
   - Ensure your Pinecone index exists and is in the correct region
   - Check that your API key has access to the index

4. **Port already in use**
   - Change the port in `run_ktp.py` or kill the process using the port
   - Default ports: Flask (5000), Streamlit (8501)

### Getting Help

- Check the logs for detailed error messages
- Verify all API keys are valid and have correct permissions
- Ensure your Pinecone index is properly configured
- Check that all required dependencies are installed

## Deployment

### Render Deployment (Recommended)

For production deployment on Render:

1. Connect your GitHub repository to Render
2. Set the environment variables in Render dashboard:
   - `OPENAI_API_KEY`
   - `PINECONE_API_KEY` 
   - `PINECONE_INDEX_NAME`
   - `GITHUB_TOKEN` (optional)
   - `NOTION_TOKEN` (optional)
   - `SLACK_BOT_TOKEN` (optional)
3. Deploy using the provided `render.yaml` configuration

The application will automatically use the production configuration when deployed.

### Local Development

For local development, you have two options:

1. **Use .env file** (for convenience):
   - Copy `env.example` to `server/.env`
   - Add your API keys to the file

2. **Use secure token management** (recommended):
   - Run the application
   - Go to the Integrations page in Streamlit
   - Input your API keys through the secure interface
   - Keys are encrypted and stored in `secure_tokens.json`

### Security Notes

- **Never commit API keys to Git** - They're excluded by `.gitignore`
- **Use environment variables in production** - Set them in your deployment platform
- **The secure token system encrypts user-input keys** - Stored locally in `secure_tokens.json`
- **Rotate API keys regularly** - Especially if they've been exposed 