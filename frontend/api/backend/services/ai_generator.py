# pyre-ignore-all-errors
from typing import List, Dict, Any
import groq
import anyio
from backend.config import get_settings

settings = get_settings()

class AIGenerator:
    """Service for generating context-aware answers using Groq LLaMA models natively async"""
    
    def __init__(self):
        # Use native AsyncGroq for seamless FastAPI integration without blocking threads
        self.client = groq.AsyncGroq(api_key=settings.groq_api_key) if settings.groq_api_key else None
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

        # 1. Prepare context string with safety truncation
        # 25k chars is ~7k-9k tokens, which fits comfortably in Groq's 12k TPM limit
        context_text = "\n\n".join([
            f"Source: {c['filename']} (Chunk {c['index']})\nContent: {c['text']}" 
            for c in context_chunks
        ])[:25000]

        # 2. Build prompt
        prompt = f"""
        You are a **Technical Knowledge Architect** for the Knowledge Transfer Platform (KTP). 
        Your goal is to provide **exhaustive, structured, and highly detailed** answers based ONLY on the provided context.

        ### TASK:
        Analyze the context chunks below and answer the user's question with maximum depth.
        - If the user asks for a **Summary of All Files**, create a clear, categorized breakdown for EVERY file mentioned in the context.
        - If the user asks a technical question, explain the "how" and "why" not just the "what."
        - Use **Markdown tables** if you encounter data that is easier to compare side-by-side.
        - NEVER make up information. If it's not in the context, say it's missing from the knowledge base.

        ### CONTEXT:
        {context_text}

        ### QUESTION: 
        {question}

        ### DETAILED RESPONSE:
        """

        try:
            # 3. Call Async Groq API natively
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior technical architect specializing in documentation synthesis and detailed technical reviews."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2048
            )
            
            answer = response.choices[0].message.content
            
            # 4. Extract unique sources
            sources = list(set([c['filename'] for c in context_chunks]))
            
            return {
                "answer": answer,
                "sources": sources,
                "confidence": 0.85 # Placeholder for actual confidence logic
            }
            
        except Exception as e:
            import traceback
            trace_str = traceback.format_exc()
            print(f"Error generating answer: {str(e)}\n{trace_str}")
            return {
                "answer": f"Error generating answer: {str(e)}",
                "sources": []
            }

# Singleton instance
ai_generator = AIGenerator()
