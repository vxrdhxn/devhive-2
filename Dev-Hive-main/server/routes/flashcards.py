from flask import Blueprint, request, jsonify
import logging
import json
import os
import uuid
from datetime import datetime
from utils.openai_utils import client, get_embedding
from utils.pinecone_utils import query_chunks, check_index_health
from utils.activity_tracker import log_system_activity

flashcards_bp = Blueprint('flashcards', __name__)
logger = logging.getLogger(__name__)

# In-memory storage for current session only (no file persistence)
current_flashcard_sets = []

@flashcards_bp.route("/generate-flashcards", methods=["POST"])
def generate_flashcards():
    """Generate flashcards from knowledge base"""
    data = request.json
    count = data.get("count", 10)

    try:
        # Check if Pinecone index is healthy
        if not check_index_health():
            return jsonify({
                "error": "Knowledge base is currently unavailable.",
                "details": "The vector database is experiencing connectivity issues."
            }), 503

        # Get content from Pinecone knowledge base
        logger.info(f"Generating {count} flashcards from knowledge base")
        
        # Query Pinecone to get diverse content for flashcard generation
        search_queries = [
            "KTP platform features",
            "vector database concepts", 
            "semantic search technology",
            "data integration process",
            "knowledge management system",
            "AI Q&A system",
            "learning path features",
            "flashcard generation",
            "GitHub integration",
            "Notion integration",
            "Slack integration",
            "deduplication system",
            "embeddings technology",
            "RAG system architecture",
            "Pinecone database",
            "OpenAI integration",
            "Flask backend",
            "Streamlit frontend"
        ]
        
        # Collect content from Pinecone with proper embedding queries
        knowledge_content = []
        seen_content_hashes = set()
        
        for query in search_queries[:min(count * 2, len(search_queries))]:
            try:
                # Get embedding for the query
                query_embedding = get_embedding(query)
                
                # Query Pinecone with the embedding
                results = query_chunks(query_embedding, top_k=3)
                
                for result in results.matches:
                    if result.metadata and result.metadata.get('text'):
                        text = result.metadata['text']
                        # Create a simple hash to avoid duplicate content
                        content_hash = hash(text[:100])
                        
                        if content_hash not in seen_content_hashes:
                            knowledge_content.append({
                                'text': text,
                                'source': result.metadata.get('source', 'Unknown'),
                                'title': result.metadata.get('title', 'Unknown'),
                                'score': result.score
                            })
                            seen_content_hashes.add(content_hash)
            except Exception as e:
                logger.warning(f"Failed to query for '{query}': {e}")
                continue
        
        # Sort by relevance score and take the best content
        knowledge_content.sort(key=lambda x: x.get('score', 0), reverse=True)
        knowledge_content = knowledge_content[:count * 2]
        
        logger.info(f"Collected {len(knowledge_content)} unique content pieces from Pinecone")
        
        # Generate flashcards based on the collected content
        flashcards = []
        seen_questions = set()
        
        for i in range(count):
            if i < len(knowledge_content):
                # Use actual knowledge base content
                content = knowledge_content[i]
                flashcard = generate_simple_flashcard_from_content(content)
            else:
                # Generate fallback flashcard
                flashcard = generate_simple_fallback_flashcard()
            
            if flashcard:
                # Check for duplicate questions
                question = flashcard.get('question', '').strip()
                if question and question not in seen_questions:
                    flashcards.append(flashcard)
                    seen_questions.add(question)
                else:
                    # Try to generate a different flashcard
                    for attempt in range(3):
                        if i < len(knowledge_content):
                            content = knowledge_content[(i + attempt) % len(knowledge_content)]
                            flashcard = generate_simple_flashcard_from_content(content)
                        else:
                            flashcard = generate_simple_fallback_flashcard()
                        
                        if flashcard:
                            question = flashcard.get('question', '').strip()
                            if question and question not in seen_questions:
                                flashcards.append(flashcard)
                                seen_questions.add(question)
                                break

        # Create flashcard set (in-memory only, no file persistence)
        set_id = str(uuid.uuid4())
        set_name = f"Flashcard Set {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        flashcard_set = {
            "id": set_id,
            "name": set_name,
            "card_count": len(flashcards),
            "created_date": datetime.now().isoformat(),
            "flashcards": flashcards
        }

        # Store in memory only (no file persistence)
        current_flashcard_sets.append(flashcard_set)

        # Log activity
        log_system_activity(f"Generated {len(flashcards)} flashcards from knowledge base", {
            "flashcard_count": len(flashcards),
            "content_sources": len(knowledge_content)
        })

        return jsonify({
            "status": "success",
            "flashcard_set": flashcard_set,
            "flashcards": flashcards,
            "set_id": set_id
        })

    except Exception as e:
        logger.error(f"Flashcard generation failed: {e}")
        return jsonify({"error": f"Flashcard generation failed: {str(e)}"}), 500

def generate_simple_flashcard_from_content(content):
    """Generate a simple Q&A flashcard from content"""
    try:
        text = content['text']
        source = content['source']
        title = content['title']
        
        # Simple prompt for Q&A
        prompt = f"""Based on this content, create a simple question and answer:

Content: {text}
Source: {source}
Title: {title}

Create a clear question and answer based on this content.

Format as JSON:
{{
    "question": "Your question here?",
    "answer": "Your answer here."
}}"""

        # Generate flashcard using OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates simple educational flashcards. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )

        # Parse the response
        content_response = response.choices[0].message.content
        try:
            import json
            flashcard = json.loads(content_response)
            return flashcard
        except json.JSONDecodeError:
            # Fallback flashcard
            return {
                "question": f"What is the main topic of: {title}?",
                "answer": f"Based on the content from {source}"
            }

    except Exception as e:
        logger.error(f"Error generating simple flashcard from content: {e}")
        return None

def generate_simple_fallback_flashcard():
    """Generate a simple fallback flashcard"""
    return {
        "question": "What is knowledge management?",
        "answer": "Knowledge management is the process of capturing, organizing, storing, and sharing knowledge within an organization."
    }

@flashcards_bp.route("/flashcard-sets", methods=["GET"])
def get_flashcard_sets():
    """Get all flashcard sets (in-memory only)"""
    try:
        return jsonify({
            "status": "success",
            "sets": current_flashcard_sets
        })
    except Exception as e:
        logger.error(f"Failed to get flashcard sets: {e}")
        return jsonify({"error": f"Failed to get flashcard sets: {str(e)}"}), 500

@flashcards_bp.route("/flashcard-sets/<set_id>", methods=["GET"])
def get_flashcard_set(set_id):
    """Get a specific flashcard set"""
    try:
        for flashcard_set in current_flashcard_sets:
            if flashcard_set["id"] == set_id:
                return jsonify({
                    "status": "success",
                    "flashcard_set": flashcard_set
                })
        
        return jsonify({"error": "Flashcard set not found"}), 404
    except Exception as e:
        logger.error(f"Failed to get flashcard set: {e}")
        return jsonify({"error": f"Failed to get flashcard set: {str(e)}"}), 500

@flashcards_bp.route("/flashcard-sets/<set_id>", methods=["DELETE"])
def delete_flashcard_set(set_id):
    """Delete a flashcard set"""
    try:
        # Find and remove the set from memory
        for i, flashcard_set in enumerate(current_flashcard_sets):
            if flashcard_set["id"] == set_id:
                deleted_set = current_flashcard_sets.pop(i)
                
                # Log activity
                log_system_activity(f"Deleted flashcard set: {deleted_set['name']}", {
                    "set_id": set_id,
                    "card_count": deleted_set.get("card_count", 0)
                })
                
                return jsonify({
                    "status": "success",
                    "message": "Flashcard set deleted successfully"
                })
        
        return jsonify({"error": "Flashcard set not found"}), 404
    except Exception as e:
        logger.error(f"Failed to delete flashcard set: {e}")
        return jsonify({"error": f"Failed to delete flashcard set: {str(e)}"}), 500

@flashcards_bp.route("/study-session", methods=["POST"])
def start_study_session():
    """Start a study session"""
    data = request.json
    set_id = data.get("set_id")
    study_mode = data.get("study_mode", "Review All")
    
    try:
        for flashcard_set in current_flashcard_sets:
            if flashcard_set["id"] == set_id:
                # Create study session
                session_id = str(uuid.uuid4())
                session = {
                    "id": session_id,
                    "set_id": set_id,
                    "study_mode": study_mode,
                    "started_at": datetime.now().isoformat(),
                    "cards": flashcard_set["flashcards"],
                    "current_card": 0,
                    "correct_answers": 0,
                    "total_answered": 0
                }
                
                # In a full implementation, you'd store this in a database
                # For now, we'll return the session data
                return jsonify({
                    "status": "success",
                    "session": session
                })
        
        return jsonify({"error": "Flashcard set not found"}), 404
    except Exception as e:
        logger.error(f"Failed to start study session: {e}")
        return jsonify({"error": f"Failed to start study session: {str(e)}"}), 500

@flashcards_bp.route("/study-session/<session_id>/answer", methods=["POST"])
def submit_answer():
    """Submit an answer for a study session"""
    data = request.json
    session_id = data.get("session_id")
    answer = data.get("answer")
    is_correct = data.get("is_correct", False)
    
    try:
        # In a full implementation, you'd update the session in a database
        # For now, we'll return a success response
        return jsonify({
            "status": "success",
            "message": "Answer recorded successfully",
            "is_correct": is_correct
        })
    except Exception as e:
        logger.error(f"Failed to submit answer: {e}")
        return jsonify({"error": f"Failed to submit answer: {str(e)}"}), 500
