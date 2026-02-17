from flask import Blueprint, request, jsonify
from utils.chunker import chunk_text
from utils.openai_utils import get_embedding
from utils.pinecone_utils import upsert_chunks
from utils.activity_tracker import log_upload_activity
import uuid
import datetime
import os
import io

# Optional PDF support
try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

ingest_bp = Blueprint('ingest', __name__)

def extract_text_from_pdf(file_content):
    """Extract text from PDF file content"""
    if not PDF_SUPPORT:
        raise Exception("PDF support not available. Install PyPDF2: pip install PyPDF2")
    
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")

@ingest_bp.route("/ingest", methods=["POST"])
def ingest():
    data = request.json
    full_text = data.get("text", "")
    metadata = data.get("metadata", {})

    if not full_text or not metadata.get("source"):
        return jsonify({"error": "Missing text or metadata.source"}), 400

    chunks = chunk_text(full_text)

    vectors = []
    for i, chunk in enumerate(chunks):
        embedding = get_embedding(chunk)
        vectors.append({
            "id": str(uuid.uuid4()),
            "values": embedding,
            "metadata": {
                **metadata,
                "text": chunk,
                "chunk_index": i,
                "timestamp": datetime.datetime.now().isoformat()
            }
        })

    upsert_chunks(vectors)
    
    # Log activity
    title = metadata.get("title", metadata.get("source", "Unknown"))
    log_upload_activity("text", title, len(vectors))
    
    return jsonify({
        "status": "success",
        "chunks_stored": len(vectors),
        "source": metadata.get("source"),
        "type": metadata.get("type")
    })

@ingest_bp.route("/ingest/file", methods=["POST"])
def ingest_file():
    """Handle file uploads (PDF, TXT)"""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # Get metadata from form data
    source = request.form.get('source', file.filename)
    doc_type = request.form.get('type', 'document')
    
    try:
        # Read file content
        file_content = file.read()
        
        # Extract text based on file type
        if file.filename.lower().endswith('.pdf'):
            if not PDF_SUPPORT:
                return jsonify({"error": "PDF support not available. Install PyPDF2: pip install PyPDF2"}), 400
            full_text = extract_text_from_pdf(file_content)
        elif file.filename.lower().endswith('.txt'):
            full_text = file_content.decode('utf-8')
        else:
            return jsonify({"error": "Unsupported file type. Use PDF or TXT"}), 400
        
        if not full_text.strip():
            return jsonify({"error": "No text content found in file"}), 400
        
        # Process the text
        chunks = chunk_text(full_text)
        
        vectors = []
        for i, chunk in enumerate(chunks):
            embedding = get_embedding(chunk)
            vectors.append({
                "id": str(uuid.uuid4()),
                "values": embedding,
                "metadata": {
                    "source": source,
                    "type": doc_type,
                    "text": chunk,
                    "chunk_index": i,
                    "timestamp": datetime.datetime.now().isoformat()
                }
            })
        
        upsert_chunks(vectors)
        
        # Log activity
        log_upload_activity("file", file.filename, len(vectors))
        
        return jsonify({
            "status": "success",
            "chunks_stored": len(vectors),
            "source": source,
            "type": doc_type,
            "filename": file.filename
        })
        
    except Exception as e:
        return jsonify({"error": f"File processing failed: {str(e)}"}), 500
