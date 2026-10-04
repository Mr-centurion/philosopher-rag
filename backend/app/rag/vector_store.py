import os
import chromadb
from typing import List, Optional, Tuple, Dict, Any
from app.config import settings
from app.rag.schema import Chunk
from app.rag.embeddings import embedding_service

class VectorStoreManager:
    def __init__(self):
        self.persist_dir = settings.CHROMA_PERSIST_DIR
        os.makedirs(self.persist_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.collection_name = "philosophy_chunks"
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        self.chunks_cache: Dict[str, Chunk] = {}

    def add_chunks(self, chunks: List[Chunk]):
        if not chunks:
            return
            
        ids = [c.id for c in chunks]
        documents = [c.text for c in chunks]
        metadatas = [
            {
                "thinker_id": c.thinker_id,
                "thinker_name": c.thinker_name,
                "tradition": c.tradition,
                "work_title": c.work_title,
                "chapter": c.chapter,
            }
            for c in chunks
        ]
        
        # Compute embeddings
        embeddings = embedding_service.embed_documents(documents)
        
        # Add / Upsert to Chroma collection
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

        for c in chunks:
            self.chunks_cache[c.id] = c

    def search(self, query: str, thinker_id: Optional[str] = None, top_k: int = 5) -> List[Tuple[Chunk, float]]:
        query_embedding = embedding_service.embed_query(query)
        
        where_filter = {"thinker_id": thinker_id} if thinker_id else None
        
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_filter
            )
        except Exception as e:
            print(f"[VectorStore] Query error: {e}")
            return []

        scored_chunks: List[Tuple[Chunk, float]] = []
        if results and "ids" in results and results["ids"]:
            doc_ids = results["ids"][0]
            distances = results.get("distances", [[]])[0]
            metas = results.get("metadatas", [[]])[0]
            docs = results.get("documents", [[]])[0]

            for i, chunk_id in enumerate(doc_ids):
                dist = distances[i] if i < len(distances) else 0.5
                # In cosine space, score = 1 - distance / 2 (or 1 - dist)
                score = max(0.0, min(1.0, 1.0 - (dist / 2.0)))
                
                meta = metas[i] if i < len(metas) else {}
                text = docs[i] if i < len(docs) else ""
                
                chunk = Chunk(
                    id=chunk_id,
                    thinker_id=meta.get("thinker_id", ""),
                    thinker_name=meta.get("thinker_name", ""),
                    tradition=meta.get("tradition", ""),
                    work_title=meta.get("work_title", ""),
                    chapter=meta.get("chapter", ""),
                    text=text,
                    score=score,
                    retrieval_source="vector"
                )
                self.chunks_cache[chunk_id] = chunk
                scored_chunks.append((chunk, score))

        return scored_chunks

vector_store = VectorStoreManager()
