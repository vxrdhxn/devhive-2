# pyre-ignore-all-errors
from typing import List, Dict, Any
import groq
import anyio
from backend.config import get_settings

settings = get_settings()

class AIGenerator:
    """Service for generating context-aware answers using Groq LLaMA models"""
    
    def __init__(self):
        self.client = groq.Groq(api_key=settings.groq_api_key) if settings.groq_api_key else None
        self.model = settings.groq_model

    async def generate_answer(
        self, 
        question: str, 
        context_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate an answer based on provided context chunks"""
        if not self.client:
            return {
                "answer": "Groq API key not configured. Please add it to your environment variables.",
                "sources": []
            }

        # 1. Prepare context string
        context_text = "\n\n".join([
            f"Source: {c['filename']} (Chunk {c['index']})\nContent: {c['text']}" 
            for c in context_chunks
        ])

        # 2. Build prompt
        prompt = f"""
        You are a helpful assistant for the Knowledge Transfer Platform (KTP). 
        Use the following pieces of context to answer the user's question. 
        If you don't know the answer based on the context, just say that you don't know, don't try to make up an answer.
        Always cite your sources.

        IMPORTANT FORMATTING RULES:
        - Organize your response using beautifully structured Markdown.
        - Use **bolding** for key terms.
        - Use bullet points or numbered lists to break down complex information.
        - ALWAYS use Markdown tables if the answer contains figures, transactions, comparatives, or tabular data.
        
        Context:
        {context_text}

        Question: {question}

        Answer:
        """

        def _sync_generate():
            try:
                # 3. Call Groq API
                client = self.client  # Local variable for type narrowing
                assert client is not None, "Groq client must be initialized"
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a professional enterprise knowledge assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    max_tokens=1024
                )
                return response
            except Exception as e:
                raise e

        try:
            response = await anyio.to_thread.run_sync(_sync_generate)
            answer = response.choices[0].message.content
            
            # 4. Extract unique sources
            sources = list(set([c['filename'] for c in context_chunks]))
            
            return {
                "answer": answer,
                "sources": sources,
                "confidence": 0.85 # Placeholder for actual confidence logic
            }
            
        except Exception as e:
            return {
                "answer": f"Error generating answer: {str(e)}",
                "sources": []
            }

# Singleton instance
ai_generator = AIGenerator()
