# 🧠 KTP - Knowledge Transfer Platform

A collaborative platform designed to simplify and streamline technical knowledge sharing within teams. KTP integrates data from multiple sources (GitHub, Notion, Slack) and provides intelligent search and Q&A capabilities powered by AI.

## ✨ Features

- **🔍 Intelligent Search**: Semantic search across all your knowledge sources
- **❓ AI-Powered Q&A**: Ask questions and get intelligent answers with sources
- **🔗 Multi-Source Integration**: Connect GitHub, Notion, and Slack
- **🔄 Automatic Deduplication**: Smart content deduplication across sources
- **📊 Real-time Analytics**: View statistics and insights about your knowledge base
- **🎨 Modern UI**: Beautiful Streamlit-based interface
- **🚀 One-Click Integration**: Integrate all sources with a single click

## 🏗️ Architecture

- **Backend**: Flask API with OpenAI embeddings and Pinecone vector database
- **Frontend**: Streamlit web application
- **AI**: OpenAI GPT-3.5-turbo for Q&A and text-embedding-3-small for embeddings
- **Database**: Pinecone vector database for semantic search
- **Integrations**: GitHub API, Notion API, Slack API

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key
- Pinecone API key
- (Optional) GitHub, Notion, and Slack tokens

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ktp
   ```

2. **Install dependencies**
   ```bash
   pip install -r server/requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp server/.env.example server/.env
   # Edit server/.env with your API keys
   ```

4. **Start the application**
   ```bash
   python run_ktp.py
   ```

## 📋 Environment Variables

Create a `.env` file in the `server` directory:

```env
# Required
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=your_pinecone_index_name

# Optional - for integrations
GITHUB_TOKEN=your_github_token
NOTION_TOKEN=your_notion_token
SLACK_BOT_TOKEN=your_slack_bot_token
```

## 🎯 Usage

### Frontend Interface

The Streamlit frontend provides an intuitive interface for:

1. **🏠 Dashboard**: System overview and quick actions
2. **📚 Knowledge Base**: Upload and manage content
3. **🔍 Search**: Search through your knowledge base
4. **❓ Q&A**: Ask questions and get AI-powered answers
5. **🔗 Integrations**: Connect external data sources
6. **📊 Statistics**: View analytics and insights

### API Endpoints

- `GET /health` - Server health check
- `POST /ingest` - Upload text content
- `POST /ingest/file` - Upload file content
- `POST /search` - Search knowledge base
- `POST /ask` - Ask questions
- `POST /integrate/github` - GitHub integration
- `POST /integrate/notion` - Notion integration
- `POST /integrate/slack` - Slack integration
- `POST /integrate/all` - One-click integration
- `GET /stats` - Get statistics

## 🔗 Integrations

### GitHub Integration
- Reads repository content (README, code files, issues)
- Supports both public and private repositories
- Automatic text file detection and processing

### Notion Integration
- Reads pages and database entries
- Supports workspace-wide page discovery
- Handles rich text and structured content

### Slack Integration
- Reads channel messages and conversation history
- Supports direct messages and search
- Automatic message content extraction

## 🧠 AI Features

### Semantic Search
- Uses OpenAI embeddings for semantic understanding
- Configurable similarity thresholds
- Source and type filtering

### Intelligent Q&A
- RAG (Retrieval-Augmented Generation) system
- Context-aware answers with source citations
- Configurable number of sources

### Content Deduplication
- MD5-based content hashing
- Source priority system (GitHub > Notion > Slack)
- Automatic duplicate detection and removal

## 📊 Analytics

The platform provides comprehensive analytics:

- Total vectors in the knowledge base
- Source breakdown (GitHub, Notion, Slack)
- Content type distribution
- Integration statistics
- Deduplication metrics

## 🛠️ Development

### Project Structure
```
ktp/
├── server/                 # Flask backend
│   ├── app.py             # Main Flask application
│   ├── routes/            # API route definitions
│   ├── utils/             # Utility modules
│   └── requirements.txt   # Python dependencies
├── frontend/              # Streamlit frontend
│   ├── streamlit_app.py   # Main Streamlit application
│   └── README.md          # Frontend documentation
├── run_ktp.py            # Startup script
└── README.md             # This file
```

### Running in Development

```bash
# Terminal 1: Start Flask backend
cd server
python app.py

# Terminal 2: Start Streamlit frontend
cd frontend
streamlit run streamlit_app.py
```

### Testing

```bash
# Test the complete system
python test_deduplication_system.py

# Test the Streamlit frontend
python test_streamlit_frontend.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for AI capabilities
- Pinecone for vector database
- Streamlit for the frontend framework
- Flask for the backend framework

## 📞 Support

For support and questions, please open an issue in the repository. 
