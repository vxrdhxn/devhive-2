from typing import Dict, Any, List
from io import BytesIO
from backend.services.document_processor import document_processor
from backend.services.chunking import chunking_service
from backend.services.embedding_service import embedding_service
from backend.auth.dependencies import supabase
import anyio

class IngestionService:
    async def process_and_store_document(
        self,
        file_content: bytes, 
        filename: str, 
        file_type: str,
        user_id: str,
        is_private: bool = False
    ) -> Dict[str, Any]:
        """Process a single document from raw bytes to chunks stored in Supabase pgvector."""
        return await self._process_and_store(
            content_source=file_content,
            filename=filename,
            file_type=file_type,
            user_id=user_id,
            is_bytes=True,
            is_private=is_private
        )

    async def process_text_content(
        self,
        text: str,
        filename: str,
        file_type: str,
        user_id: str,
        metadata: Dict[str, Any] = None,
        is_private: bool = False
    ) -> Dict[str, Any]:
        """Process raw text content (e.g. from integrations) to chunks stored in Supabase."""
        return await self._process_and_store(
            content_source=text,
            filename=filename,
            file_type=file_type,
            user_id=user_id,
            is_bytes=False,
            extra_metadata=metadata or {},
            is_private=is_private
        )

    async def _process_and_store(
        self,
        content_source: Any,
        filename: str,
        file_type: str,
        user_id: str,
        is_bytes: bool = True,
        extra_metadata: Dict[str, Any] = None,
        is_private: bool = False
    ) -> Dict[str, Any]:
        """Core logic for indexing content."""
        if not supabase:
            raise ValueError("Supabase client is not initialized.")

        # 1. Insert Document record
        doc_data = {
            'filename': filename,
            'file_type': file_type,
            'uploaded_by': user_id,
            'status': 'processing',
            'is_private': is_private,
            'metadata': extra_metadata or {}
        }
        doc_response = await anyio.to_thread.run_sync(
            lambda: supabase.table('documents').insert(doc_data).execute()
        )
        
        if not doc_response or not doc_response.data:
            raise RuntimeError("Failed to create document record.")
            
        doc_id = doc_response.data[0]['id']

        try:
            # 2. Extract Text if bytes, else use content_source directly
            if is_bytes:
                await anyio.to_thread.run_sync(
                    lambda: supabase.table('documents').update({'status': 'extracting text'}).eq('id', doc_id).execute()
                )
                full_text = await anyio.to_thread.run_sync(
                    lambda: document_processor.extract_text(content_source, filename)
                )
            else:
                full_text = content_source
            
            # 3. Chunk Text
            await anyio.to_thread.run_sync(
                lambda: supabase.table('documents').update({'status': 'chunking content'}).eq('id', doc_id).execute()
            )
            chunks = await anyio.to_thread.run_sync(
                lambda: chunking_service.chunk_text(full_text, chunk_size=800, chunk_overlap=150)
            )
            
            if not chunks:
                raise ValueError("No text could be extracted or chunked from document.")
            
            # 4. Generate Embeddings (batch)
            await anyio.to_thread.run_sync(
                lambda: supabase.table('documents').update({'status': f'generating {len(chunks)} embeddings'}).eq('id', doc_id).execute()
            )
            embeddings = await embedding_service.batch_generate_embeddings(chunks)
            
            # --- CONTENT DEDUPLICATION CHECK ---
            # Using the first chunk's embedding to check for near-identical documents
            if embeddings:
                first_chunk_embedding = embeddings[0]
                similarity_res = await anyio.to_thread.run_sync(
                    lambda: supabase.rpc(
                        'match_chunks', 
                        {
                            'query_embedding': first_chunk_embedding,
                            'match_threshold': 0.95,
                            'match_count': 1,
                            'requesting_user_id': user_id
                        }
                    ).execute()
                )
                
                if similarity_res.data and len(similarity_res.data) > 0:
                    matched_doc_id = similarity_res.data[0].get('document_id')
                    print(f"DEBUG: DUPLICATE DETECTED! Found match with document {matched_doc_id}")
                    
                    await anyio.to_thread.run_sync(
                        lambda: supabase.table('documents').update({
                            'status': 'duplicate',
                            'metadata': {** (extra_metadata or {}), 'duplicate_of': matched_doc_id}
                        }).eq('id', doc_id).execute()
                    )
                    
                    return {
                        "status": "duplicate",
                        "document_id": doc_id,
                        "matched_document_id": matched_doc_id,
                        "message": f"Content already exists in the knowledge base (matched ID: {matched_doc_id})"
                    }
            # -----------------------------------
            
            # 5. Insert Chunks into Supabase
            await anyio.to_thread.run_sync(
                lambda: supabase.table('documents').update({'status': 'storing in vector db'}).eq('id', doc_id).execute()
            )
            chunk_records = []
            for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_records.append({
                    'document_id': doc_id,
                    'content': chunk_text,
                    'embedding': embedding,
                    'metadata': {'index': i}
                })
            
            await anyio.to_thread.run_sync(
                lambda: supabase.table('chunks').insert(chunk_records).execute()
            )
            
            # 6. Mark Document Complete
            await anyio.to_thread.run_sync(
                lambda: supabase.table('documents').update({
                    'status': 'completed'
                }).eq('id', doc_id).execute()
            )
            
            return {"status": "success", "document_id": doc_id, "chunks_processed": len(chunks)}
            
        except Exception as e:
            # Mark document as failed
            await anyio.to_thread.run_sync(
                lambda: supabase.table('documents').update({
                    'status': 'error',
                    'metadata': {'error_message': str(e)}
                }).eq('id', doc_id).execute()
            )
            raise e

ingestion_service = IngestionService()
