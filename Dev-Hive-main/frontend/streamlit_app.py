#!/usr/bin/env python3
"""
KTP - Knowledge Transfer Platform
Streamlit Frontend
"""

import streamlit as st
import requests
import json
import time
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
# API base URL - use localhost for local development, environment variable for production
API_BASE = os.getenv("FLASK_API_URL", "http://localhost:5000")

def main():
    st.set_page_config(
        page_title="DevHive - Unified Knowledge Hub",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: left;
        margin-bottom: 1rem;
        margin-top: 0;
        padding-top: 0;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #f5c6cb;
    }
    .info-message {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #bee5eb;
    }
    /* Reduce top margin for the main container */
    .main .block-container {
        padding-top: 1rem;
    }
    /* Navigation button styling - only for sidebar navigation */
    [data-testid="stSidebar"] .stButton > button {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 8px;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        border-color: #667eea;
    }
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    /* Navigation button highlighting */
    .nav-button-active {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%) !important;
        border-color: #28a745 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">🧠 DevHive - Unified Knowledge Hub</h1>', unsafe_allow_html=True)
    st.markdown("A collaborative platform designed to simplify and streamline technical knowledge sharing within teams.")
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Navigation")
        
        # Convert dropdown to separate buttons
        st.markdown("**Choose a page:**")
        
        # Navigation buttons with better styling
        if st.button("🏠 Dashboard", use_container_width=True, key="nav_dashboard"):
            st.session_state.current_page = "🏠 Dashboard"
        
        if st.button("📚 Knowledge Base", use_container_width=True, key="nav_knowledge"):
            st.session_state.current_page = "📚 Knowledge Base"
        
        if st.button("🔍 Search", use_container_width=True, key="nav_search"):
            st.session_state.current_page = "🔍 Search"
        
        if st.button("❓ Q&A", use_container_width=True, key="nav_qa"):
            st.session_state.current_page = "❓ Q&A"
        
        if st.button("🔗 Integrations", use_container_width=True, key="nav_integrations"):
            st.session_state.current_page = "🔗 Integrations"
        
        if st.button("🎯 Learning Path", use_container_width=True, key="nav_learning"):
            st.session_state.current_page = "🎯 Learning Path"
        
        # Initialize current page if not set
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "🏠 Dashboard"
        
        st.divider()
        
        st.header("⚡ Quick Actions")
        if st.button("🔄 Check Server Health"):
            check_health()
        if st.button("🚀 One-Click Integration"):
            # Check if we have stored tokens
            github_status = get_token_status("github")
            notion_status = get_token_status("notion")
            slack_status = get_token_status("slack")
            
            if not any([github_status.get("has_token"), notion_status.get("has_token"), slack_status.get("has_token")]):
                st.error("❌ No tokens stored. Please store at least one token in the Integrations page first.")
            else:
                integrate_all_sources()
    
    # Page routing based on session state
    page = st.session_state.current_page
    
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "📚 Knowledge Base":
        show_knowledge_base()
    elif page == "🔍 Search":
        show_search()
    elif page == "❓ Q&A":
        show_qa()
    elif page == "🔗 Integrations":
        show_integrations()
    elif page == "🎯 Learning Path":
        show_learning_path()

def check_health():
    """Check server health"""
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            st.sidebar.success("✅ Server is running!")
        else:
            st.sidebar.error("❌ Server health check failed")
    except:
        st.sidebar.error("❌ Cannot connect to server")

def show_dashboard():
    """Show the main dashboard"""
    st.header("🏠 Dashboard")
    
    # Welcome message
    st.markdown("""
    ### Welcome to DevHive - Unified Knowledge Hub! 🧠
    
    This platform helps you manage and access knowledge from multiple sources including GitHub repositories, Notion workspaces, and Slack conversations.
    
    **Get started by:**
    - 📚 **Uploading content** in the Knowledge Base section
    - 🔍 **Searching** through your knowledge base
    - ❓ **Asking questions** to get AI-powered answers
    - 🔗 **Integrating** external data sources
    - 🎯 **Creating flashcards** for systematic learning
    """)
    
    # Recent activity
    st.subheader("📈 Recent Activity")
    show_activity_timeline()

def show_knowledge_base():
    """Show knowledge base management"""
    st.header("📚 Knowledge Base")
    
    # Upload section
    st.subheader("📤 Upload Content")
    
    tab1, tab2 = st.tabs(["📄 Text Input", "📁 File Upload"])
    
    with tab1:
        title = st.text_input("Document Title")
        content = st.text_area("Content", height=200)
        
        if st.button("📤 Upload Text"):
            if title and content:
                upload_text(title, content)
            else:
                st.error("Please provide both title and content")
    
    with tab2:
        uploaded_file = st.file_uploader("Choose a file", type=['txt', 'pdf'])
        if uploaded_file is not None:
            st.write("File uploaded:", uploaded_file.name)
            if st.button("📤 Upload File"):
                upload_file(uploaded_file)

def show_search():
    """Show search functionality"""
    st.header("🔍 Search Knowledge Base")
    
    # Search input
    search_query = st.text_input("Enter your search query:", placeholder="Search for knowledge...")
    
    if search_query:
        if st.button("🔍 Search"):
            search_knowledge(search_query)
    
    # Search filters
    with st.expander("🔧 Search Filters"):
        col1, col2 = st.columns(2)
        
        with col1:
            source_filter = st.selectbox(
                "Source:",
                ["All", "GitHub", "Notion", "Slack", "Uploaded"]
            )
        
        with col2:
            type_filter = st.selectbox(
                "Type:",
                ["All", "Documentation", "Code", "Issue", "Message"]
            )

def show_qa():
    """Show Q&A functionality"""
    st.header("❓ Ask Questions")
    
    # Question input
    question = st.text_area("Ask a question:", placeholder="What would you like to know?", height=100)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        top_k = st.slider("Number of sources to use:", min_value=1, max_value=10, value=5)
    
    with col2:
        ask_button = st.button("🤖 Ask", use_container_width=True)
    
    # Handle ask button click outside of column
    if ask_button:
        if question:
            ask_question(question, top_k)
        else:
            st.error("Please enter a question")
    
    # Example questions
    st.subheader("💡 Example Questions")
    
    example_questions = [
        "What is KTP?",
        "What features are being developed?",
        "What is the tech stack?",
        "What integrations are available?",
        "What issues are being discussed?"
    ]
    
    cols = st.columns(len(example_questions))
    for i, example_q in enumerate(example_questions):
        with cols[i]:
            if st.button(example_q, use_container_width=True):
                ask_question(example_q, top_k)

def show_integrations():
    """Show integration management"""
    st.header("🔗 Data Integrations")
    
    # Integration status
    st.subheader("📊 Integration Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        github_status = get_token_status("github")
        st.metric("GitHub", "✅ Token Stored" if github_status.get("has_token") else "❌ No Token")
    
    with col2:
        notion_status = get_token_status("notion")
        st.metric("Notion", "✅ Token Stored" if notion_status.get("has_token") else "❌ No Token")
    
    with col3:
        slack_status = get_token_status("slack")
        st.metric("Slack", "✅ Token Stored" if slack_status.get("has_token") else "❌ No Token")
    
    # Integration tabs
    tab1, tab2, tab3 = st.tabs(["📦 GitHub", "📝 Notion", "💬 Slack"])
    
    with tab1:
        st.subheader("📦 GitHub Integration")
        st.write("Connect to GitHub repositories to import code, documentation, and issues.")
        
        # GitHub configuration
        with st.expander("🔧 GitHub Configuration", expanded=True):
            github_token = st.text_input(
                "GitHub API Token:", 
                type="password",
                help="Your GitHub personal access token. Get it from GitHub Settings > Developer settings > Personal access tokens"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                owner = st.text_input("Repository Owner:", value="nannndini")
            with col2:
                repo = st.text_input("Repository Name:", value="KTP")
        
        # Token management
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔐 Store Token", use_container_width=True):
                if github_token:
                    store_token("github", github_token)
                else:
                    st.error("Please provide GitHub token")
        
        with col2:
            if st.button("🗑️ Remove Token", use_container_width=True):
                remove_token("github")
        
        # Integration button
        if st.button("📦 Integrate GitHub Repository", use_container_width=True):
            if owner and repo:
                # Check if token is stored
                token_status = get_token_status("github")
                if token_status.get("has_token"):
                    integrate_github(owner, repo)
                else:
                    st.error("Please store a GitHub token first")
            else:
                st.error("Please provide repository owner and name")
    
    with tab2:
        st.subheader("📝 Notion Integration")
        st.write("Connect to Notion workspace to import pages and databases.")
        
        # Notion configuration
        with st.expander("🔧 Notion Configuration", expanded=True):
            notion_token = st.text_input(
                "Notion API Key:", 
                type="password",
                help="Your Notion integration token. Get it from https://www.notion.so/my-integrations"
            )
            
            read_all_workspace = st.checkbox("Read All Workspace Pages", value=True)
            
            if not read_all_workspace:
                search_query = st.text_input("Search Query (optional):")
                
                col1, col2 = st.columns(2)
                with col1:
                    page_ids = st.text_input("Page IDs (comma-separated):")
                with col2:
                    database_ids = st.text_input("Database IDs (comma-separated):")
        
        # Token management
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔐 Store Token", key="notion_store"):
                if notion_token:
                    store_token("notion", notion_token)
                else:
                    st.error("Please provide Notion token")
        
        with col2:
            if st.button("🗑️ Remove Token", key="notion_remove"):
                remove_token("notion")
        
        # Integration button
        if st.button("📝 Integrate Notion Workspace", use_container_width=True):
            # Check if token is stored
            token_status = get_token_status("notion")
            if token_status.get("has_token"):
                if read_all_workspace:
                    integrate_notion("", True, [], [])
                else:
                    page_ids_list = [pid.strip() for pid in page_ids.split(",")] if page_ids else []
                    database_ids_list = [did.strip() for did in database_ids.split(",")] if database_ids else []
                    integrate_notion(search_query, False, page_ids_list, database_ids_list)
            else:
                st.error("Please store a Notion token first")
    
    with tab3:
        st.subheader("💬 Slack Integration")
        st.write("Connect to Slack workspace to import channel messages and conversations.")
        
        # Slack configuration
        with st.expander("🔧 Slack Configuration", expanded=True):
            slack_token = st.text_input(
                "Slack Bot Token:", 
                type="password",
                help="Your Slack bot user OAuth token. Get it from https://api.slack.com/apps"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                channel_ids = st.text_input("Channel IDs (comma-separated, optional):")
            with col2:
                include_dms = st.checkbox("Include Direct Messages")
            
            search_query = st.text_input("Search Query (optional):")
        
        # Token management
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔐 Store Token", key="slack_store"):
                if slack_token:
                    store_token("slack", slack_token)
                else:
                    st.error("Please provide Slack token")
        
        with col2:
            if st.button("🗑️ Remove Token", key="slack_remove"):
                remove_token("slack")
        
        # Integration button
        if st.button("💬 Integrate Slack Workspace", use_container_width=True):
            # Check if token is stored
            token_status = get_token_status("slack")
            if token_status.get("has_token"):
                channel_ids_list = [cid.strip() for cid in channel_ids.split(",")] if channel_ids else []
                integrate_slack(channel_ids_list, search_query, include_dms)
            else:
                st.error("Please store a Slack token first")

def show_learning_path():
    """Show learning path with flashcards"""
    st.header("🎯 Learning Path")
    
    # Learning path overview
    st.markdown("""
    ### Master Your Knowledge with Interactive Flashcards! 🎯
    
    Transform your integrated knowledge into bite-sized learning modules. Review concepts, test your understanding, and track your progress.
    """)
    
    # Check if we have data to create flashcards from
    try:
        response = requests.get(f"{API_BASE}/stats")
        has_data = False
        if response.status_code == 200:
            stats = response.json().get("stats", {})
            total_vectors = stats.get("total_vectors", 0)
            has_data = total_vectors > 0
            
            if has_data:
                st.success(f"✅ Found {total_vectors} knowledge chunks to create flashcards from!")
            else:
                st.warning("⚠️ No knowledge data found. Please integrate some data sources first.")
    except:
        st.warning("⚠️ Cannot check knowledge base status. Please ensure the server is running.")
        has_data = False
    
    if not has_data:
        st.info("💡 **To get started:**\n1. Go to **Integrations** and connect your data sources\n2. Or upload content in **Knowledge Base**\n3. Then return here to create your learning path!")
        return
    
    # Show session-only notice
    st.info("💡 **Note:** Flashcard sets are session-only and will be cleared when you restart the app.")
    
    # Only show Create Flashcards section
    show_create_flashcards()

def show_create_flashcards():
    """Show simplified flashcard creation interface"""
    st.subheader("📝 Create Flashcards")
    
    # Only show number of flashcards option
    flashcard_count = st.slider("Number of flashcards to generate:", min_value=5, max_value=50, value=10)
    
    # Generate flashcards button
    if st.button("🎯 Generate Flashcards", use_container_width=True):
        generate_flashcards_simplified(flashcard_count)
    
    # Show existing flashcards
    # st.subheader("📚 Your Flashcard Sets")
    # show_existing_flashcards()

def generate_flashcards_simplified(count):
    """Generate flashcards with simplified options"""
    try:
        with st.spinner("🎯 Generating flashcards from your knowledge base..."):
            response = requests.post(f"{API_BASE}/generate-flashcards", json={
                "count": count
            })
        
        if response.status_code == 200:
            result = response.json()
            flashcards = result.get('flashcards', [])
            set_id = result.get('set_id')
            
            st.success(f"✅ Generated {len(flashcards)} flashcards!")
            
            # Show flashcards directly without expandable sections
            if flashcards:
                st.subheader("📝 Generated Flashcards")
                
                # Remove duplicates based on question content
                unique_flashcards = []
                seen_questions = set()
                
                for card in flashcards:
                    question = card.get('question', '').strip()
                    if question and question not in seen_questions:
                        unique_flashcards.append(card)
                        seen_questions.add(question)
                
                # Display flashcards in a simple format
                for i, card in enumerate(unique_flashcards):
                    st.write(f"**Question {i+1}:** {card.get('question', '')}")
                    st.write(f"**Answer:** {card.get('answer', '')}")
                    st.write("---")
                
                # Simple summary
                st.info(f"Generated {len(unique_flashcards)} unique flashcards from your knowledge base.")
        else:
            error_msg = response.json().get('error', 'Unknown error')
            st.error(f"❌ Failed to generate flashcards: {error_msg}")
                
    except Exception as e:
        st.error(f"❌ Error generating flashcards: {e}")

def get_flashcard_sets():
    """Get available flashcard sets"""
    try:
        response = requests.get(f"{API_BASE}/flashcard-sets")
        if response.status_code == 200:
            sets = response.json().get('sets', [])
            return [f"{s['name']} ({s['card_count']} cards)" for s in sets]
        else:
            return []
    except:
        return []

def show_existing_flashcards():
    """Show existing flashcard sets with simplified display"""
    try:
        response = requests.get(f"{API_BASE}/flashcard-sets")
        if response.status_code == 200:
            sets = response.json().get('sets', [])
            
            if not sets:
                st.info("📭 No flashcard sets created yet. Generate your first set above!")
                st.info("💡 **Note:** Flashcard sets are session-only and will be cleared when you restart the app.")
                return
            
            st.subheader(f"📚 Your Flashcard Sets ({len(sets)} total)")
            st.info("💡 **Note:** Flashcard sets are session-only and will be cleared when you restart the app.")
            
            for flashcard_set in sets:
                with st.expander(f"📋 {flashcard_set['name']} ({flashcard_set['card_count']} cards)"):
                    # Basic set information
                    st.write(f"**📅 Created:** {flashcard_set.get('created_date', 'Unknown')}")
                    
                    # Show sample cards if available
                    cards = flashcard_set.get('cards', [])
                    if cards:
                        st.write("**📄 Sample Cards:**")
                        for i, card in enumerate(cards[:3]):  # Show first 3
                            st.write(f"  {i+1}. **Q:** {card.get('question', '')[:80]}...")
                            st.write(f"     **A:** {card.get('answer', '')[:80]}...")
                    
                    # Simple action buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"🗑️ Delete Set", key=f"delete_{flashcard_set['id']}"):
                            delete_flashcard_set(flashcard_set['id'])
        else:
            st.error("❌ Failed to load flashcard sets")
    except Exception as e:
        st.error(f"❌ Error loading flashcard sets: {e}")

def delete_flashcard_set(set_id):
    """Delete a flashcard set"""
    try:
        response = requests.delete(f"{API_BASE}/flashcard-sets/{set_id}")
        if response.status_code == 200:
            st.success("✅ Flashcard set deleted!")
            st.rerun()
        else:
            st.error("❌ Failed to delete flashcard set")
    except Exception as e:
        st.error(f"❌ Error deleting flashcard set: {e}")

def show_activity_timeline():
    """Show activity timeline"""
    try:
        response = requests.get(f"{API_BASE}/activities")
        if response.status_code == 200:
            data = response.json()
            activities = data.get("activities", [])
            
            if not activities:
                st.info("No activities recorded yet. Start using the platform to see your timeline!")
                return
            
            # Display timeline
            for activity in activities:
                activity_type = activity.get("type", "")
                description = activity.get("description", "")
                time_ago = activity.get("time_ago", "")
                details = activity.get("details", {})
                
                # Create timeline item
                with st.container():
                    col1, col2 = st.columns([1, 4])
                    
                    with col1:
                        # Activity icon based on type
                        if activity_type == "integration":
                            st.markdown("🔗")
                        elif activity_type == "upload":
                            st.markdown("📤")
                        elif activity_type == "search":
                            st.markdown("🔍")
                        elif activity_type == "qa":
                            st.markdown("❓")
                        elif activity_type == "system":
                            st.markdown("⚙️")
                        else:
                            st.markdown("📝")
                    
                    with col2:
                        # Activity details
                        st.markdown(f"**{description}**")
                        st.caption(f"🕒 {time_ago}")
                        
                        # Show additional details if available
                        if details:
                            if "chunks_stored" in details:
                                st.caption(f"📊 {details['chunks_stored']} chunks stored")
                            if "duplicates_removed" in details and details["duplicates_removed"] > 0:
                                st.caption(f"🗑️ {details['duplicates_removed']} duplicates removed")
                            if "results_count" in details:
                                st.caption(f"🔍 {details['results_count']} results found")
                            if "sources_used" in details:
                                st.caption(f"📚 {details['sources_used']} sources used")
                
                # Add separator
                st.divider()
        
        else:
            st.error("Failed to retrieve activities")
    except Exception as e:
        st.error(f"Error retrieving activities: {e}")

# API Functions
def upload_text(title, content):
    """Upload text content"""
    try:
        response = requests.post(f"{API_BASE}/ingest", json={
            "title": title,
            "content": content
        })
        
        if response.status_code == 200:
            st.success("✅ Text uploaded successfully!")
        else:
            st.error(f"❌ Upload failed: {response.json().get('error', 'Unknown error')}")
    except Exception as e:
        st.error(f"❌ Upload error: {e}")

def upload_file(file):
    """Upload file content"""
    try:
        files = {"file": file}
        response = requests.post(f"{API_BASE}/ingest/file", files=files)
        
        if response.status_code == 200:
            st.success("✅ File uploaded successfully!")
        else:
            st.error(f"❌ Upload failed: {response.json().get('error', 'Unknown error')}")
    except Exception as e:
        st.error(f"❌ Upload error: {e}")

def search_knowledge(query):
    """Search knowledge base"""
    try:
        response = requests.post(f"{API_BASE}/search", json={"query": query})
        
        if response.status_code == 200:
            results = response.json()
            search_results = results.get("results", [])
            
            if search_results:
                # Get the result with the highest score
                best_result = max(search_results, key=lambda x: x.get('score', 0))
                
                st.subheader(f"🔍 Best Answer for: '{query}'")
                
                # Display the best answer directly
                st.write("**Answer:**")
                st.write(best_result.get("text", ""))
            else:
                st.warning("⚠️ No relevant results found for your search query.")
                st.info("💡 Try rephrasing your search or check if you have integrated any data sources.")
        elif response.status_code == 429:
            error_data = response.json()
            st.error(f"⚠️ {error_data.get('error', 'Rate limit exceeded')}")
            st.info(f"💡 {error_data.get('details', 'Please wait a moment and try again.')}")
        elif response.status_code == 503:
            error_data = response.json()
            st.error(f"🔧 {error_data.get('error', 'Service temporarily unavailable')}")
            st.info(f"💡 {error_data.get('details', 'The vector database is experiencing issues. Please try again in a few minutes.')}")
        else:
            error_data = response.json()
            st.error(f"❌ Search failed: {error_data.get('error', 'Unknown error')}")
            if 'details' in error_data:
                st.info(f"💡 {error_data.get('details')}")
    except Exception as e:
        st.error(f"❌ Search error: {e}")
        st.info("💡 This might be a temporary connectivity issue. Please try again.")

def ask_question(question, top_k=5):
    """Ask a question"""
    try:
        with st.spinner("🤖 Thinking..."):
            response = requests.post(f"{API_BASE}/ask", json={
                "question": question,
                "top_k": top_k
            })
        
        if response.status_code == 200:
            result = response.json()
            
            st.subheader("🤖 Answer")
            st.write(result.get("answer", ""))
            
            # Sources
            sources = result.get("sources", [])
            if sources:
                st.subheader("📚 Sources")
                for i, source in enumerate(sources):
                    with st.expander(f"📄 Source {i+1} (Score: {source.get('score', 0):.3f})"):
                        st.write("**Content:**")
                        st.write(source.get("text", ""))
                        st.write(f"**Source:** {source.get('source', 'Unknown')}")
        elif response.status_code == 429:
            error_data = response.json()
            st.error(f"⚠️ {error_data.get('error', 'Rate limit exceeded')}")
            st.info(f"💡 {error_data.get('details', 'Please wait a moment and try again.')}")
        elif response.status_code == 503:
            error_data = response.json()
            st.error(f"🔧 {error_data.get('error', 'Service temporarily unavailable')}")
            st.info(f"💡 {error_data.get('details', 'The knowledge base is experiencing issues. Please try again in a few minutes.')}")
        else:
            error_data = response.json()
            st.error(f"❌ Q&A failed: {error_data.get('error', 'Unknown error')}")
            if 'details' in error_data:
                st.info(f"💡 {error_data.get('details')}")
    except Exception as e:
        st.error(f"❌ Q&A error: {e}")
        st.info("💡 This might be a temporary connectivity issue. Please try again.")

def integrate_all_sources():
    """Integrate all sources with enhanced feedback"""
    try:
        # Show integration status
        with st.spinner("🚀 Integrating all available sources..."):
            response = requests.post(f"{API_BASE}/integrate/all", json={})
        
        if response.status_code == 200:
            result = response.json()
            
            st.success("✅ One-Click Integration completed successfully!")
            
            # Show comprehensive results
            st.subheader("📊 Integration Results")
            
            # Main metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                sources_count = len(result.get("sources_integrated", []))
                st.metric("Sources Integrated", sources_count)
            
            with col2:
                chunks_processed = result.get("total_chunks_processed", 0)
                st.metric("Chunks Processed", chunks_processed)
            
            with col3:
                chunks_stored = result.get("total_chunks_stored", 0)
                st.metric("Chunks Stored", chunks_stored)
            
            with col4:
                duplicates_removed = result.get("total_duplicates_removed", 0)
                st.metric("Duplicates Removed", duplicates_removed)
            
            # Show individual source results
            results = result.get("results", [])
            if results:
                st.subheader("🔍 Individual Source Results")
                
                for integration_result in results:
                    if integration_result.get("success"):
                        source_name = integration_result.get('integration', 'Unknown').title()
                        chunks_stored = integration_result.get('chunks_stored', 0)
                        chunks_processed = integration_result.get('chunks_processed', 0)
                        duplicates_removed = integration_result.get('duplicates_removed', 0)
                        
                        st.success(f"✅ **{source_name}**: {chunks_stored} chunks stored ({chunks_processed} processed, {duplicates_removed} duplicates removed)")
                    else:
                        source_name = integration_result.get('integration', 'Unknown').title()
                        error_msg = integration_result.get('error', 'Unknown error')
                        st.error(f"❌ **{source_name}**: {error_msg}")
            
            # Show next steps
            if chunks_stored > 0:
                st.subheader("🎯 Next Steps")
                st.info("""
                **Great! Your knowledge base is now populated. You can:**
                - 🔍 **Search** for specific information in the Search page
                - ❓ **Ask questions** in the Q&A page
                - 🎯 **Create flashcards** in the Learning Path page
                """)
            else:
                st.warning("⚠️ No new data was integrated. Check your API tokens and permissions.")
                
        else:
            error_msg = response.json().get('error', 'Unknown error')
            st.error(f"❌ Integration failed: {error_msg}")
            
            # Provide troubleshooting tips
            st.subheader("🔧 Troubleshooting")
            st.info("""
            **Common issues:**
            - Check that your API tokens are set in the environment variables
            - Ensure your tokens have the correct permissions
            - Verify that the data sources are accessible
            """)
            
    except Exception as e:
        st.error(f"❌ Integration error: {e}")
        st.info("💡 Make sure the server is running and accessible.")

def integrate_github(owner, repo):
    """Integrate GitHub repository"""
    try:
        with st.spinner(f"📦 Integrating GitHub: {owner}/{repo}"):
            response = requests.post(f"{API_BASE}/integrate/github", json={
                "owner": owner,
                "repo": repo
            })
        
        if response.status_code == 200:
            result = response.json()
            st.success(f"✅ GitHub integration completed! {result.get('chunks_stored', 0)} chunks stored")
        else:
            st.error(f"❌ GitHub integration failed: {response.json().get('error', 'Unknown error')}")
    except Exception as e:
        st.error(f"❌ GitHub integration error: {e}")

def integrate_notion(search_query, read_all_workspace, page_ids, database_ids):
    """Integrate Notion data"""
    try:
        config = {"read_all_workspace": read_all_workspace}
        
        if search_query:
            config["search_query"] = search_query
        
        if page_ids:
            config["page_ids"] = [pid.strip() for pid in page_ids.split(",")]
        
        if database_ids:
            config["database_ids"] = [did.strip() for did in database_ids.split(",")]
        
        with st.spinner("📝 Integrating Notion data..."):
            response = requests.post(f"{API_BASE}/integrate/notion", json=config)
        
        if response.status_code == 200:
            result = response.json()
            st.success(f"✅ Notion integration completed! {result.get('chunks_stored', 0)} chunks stored")
        else:
            st.error(f"❌ Notion integration failed: {response.json().get('error', 'Unknown error')}")
    except Exception as e:
        st.error(f"❌ Notion integration error: {e}")

def integrate_slack(channel_ids, search_query, include_dms):
    """Integrate Slack data"""
    try:
        config = {"include_dms": include_dms}
        
        if channel_ids:
            config["channel_ids"] = [cid.strip() for cid in channel_ids.split(",")]
        
        if search_query:
            config["search_query"] = search_query
        
        with st.spinner("💬 Integrating Slack data..."):
            response = requests.post(f"{API_BASE}/integrate/slack", json=config)
        
        if response.status_code == 200:
            result = response.json()
            st.success(f"✅ Slack integration completed! {result.get('chunks_stored', 0)} chunks stored")
        else:
            st.error(f"❌ Slack integration failed: {response.json().get('error', 'Unknown error')}")
    except Exception as e:
        st.error(f"❌ Slack integration error: {e}")

def store_token(service, token):
    """Store a token for a service"""
    try:
        response = requests.post(f"{API_BASE}/tokens/store", json={
            "service": service,
            "token": token
        })
        
        if response.status_code == 200:
            result = response.json()
            st.success(f"✅ {service.title()} token stored successfully!")
            st.rerun()
        else:
            error_msg = response.json().get('error', 'Unknown error')
            st.error(f"❌ Failed to store {service} token: {error_msg}")
    except Exception as e:
        st.error(f"❌ Error storing {service} token: {e}")

def remove_token(service):
    """Remove a token for a service"""
    try:
        response = requests.delete(f"{API_BASE}/tokens/remove/{service}")
        
        if response.status_code == 200:
            st.success(f"✅ {service.title()} token removed successfully!")
            st.rerun()
        else:
            error_msg = response.json().get('error', 'Unknown error')
            st.error(f"❌ Failed to remove {service} token: {error_msg}")
    except Exception as e:
        st.error(f"❌ Error removing {service} token: {e}")

def get_token_status(service):
    """Get token status for a service"""
    try:
        response = requests.get(f"{API_BASE}/tokens/get/{service}")
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"has_token": False}
    except Exception as e:
        return {"has_token": False}

if __name__ == "__main__":
    main() 