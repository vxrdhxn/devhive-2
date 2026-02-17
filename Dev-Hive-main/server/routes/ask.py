from flask import Blueprint, request, jsonify
import logging
from utils.openai_utils import get_embedding, client
from utils.pinecone_utils import query_chunks, check_index_health
from utils.activity_tracker import log_qa_activity

ask_bp = Blueprint('ask', __name__)
logger = logging.getLogger(__name__)

@ask_bp.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question", "")
    top_k = data.get("top_k", 5)
    metadata_filter = data.get("filter", None)

    if not question:
        return jsonify({"error": "Missing question parameter"}), 400

    try:
        # First check if Pinecone index is healthy
        if not check_index_health():
            return jsonify({
                "error": "Knowledge base is currently unavailable. Please try again later.",
                "details": "The vector database is experiencing connectivity issues."
            }), 503

        # Get embedding for the question
        logger.info(f"Getting embedding for question: {question[:50]}...")
        question_embedding = get_embedding(question)
        
        # Search for relevant context with retry logic
        logger.info(f"Searching for {top_k} relevant chunks...")
        results = query_chunks(question_embedding, top_k=top_k, metadata_filter=metadata_filter)
        
        # Build context from retrieved chunks
        context = "\n\n".join([match.metadata.get("text", "") for match in results.matches])
        
        # Create prompt for OpenAI
        prompt = f"""Based on the following context, please answer the question. If the context doesn't contain enough information to answer the question, say so.

Context:
{context}

Question: {question}

Answer:"""
        
        # Get answer from OpenAI
        logger.info("Generating answer with OpenAI...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        answer = response.choices[0].message.content
        
        # Format sources
        sources = []
        for match in results.matches:
            sources.append({
                "text": match.metadata.get("text", ""),
                "source": match.metadata.get("source", ""),
                "score": match.score
            })
        
        logger.info(f"Q&A completed successfully with {len(sources)} sources")
        
        # Log Q&A activity
        log_qa_activity(question, len(sources))
        
        return jsonify({
            "status": "success",
            "question": question,
            "answer": answer,
            "sources": sources,
            "context_used": len(results.matches)
        })
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Q&A failed: {error_msg}")
        
        # Provide specific error messages for common issues
        if "too many" in error_msg.lower() or "rate limit" in error_msg.lower():
            return jsonify({
                "error": "Service rate limit exceeded. Please wait a moment and try again.",
                "details": "Too many requests to the knowledge base. Please slow down your requests."
            }), 429
        elif "500" in error_msg or "internal server error" in error_msg.lower():
            return jsonify({
                "error": "Knowledge base service temporarily unavailable.",
                "details": "The Q&A service is experiencing issues. Please try again in a few minutes."
            }), 503
        elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
            return jsonify({
                "error": "Unable to connect to knowledge base service.",
                "details": "Network connectivity issues with the vector database."
            }), 503
        else:
            return jsonify({
                "error": f"Q&A failed: {error_msg}",
                "details": "An unexpected error occurred during the Q&A operation."
            }), 500
