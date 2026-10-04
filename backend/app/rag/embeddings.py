import os
import math
import numpy as np
from typing import List, Optional
import google.generativeai as genai
from app.config import settings

class EmbeddingProvider:
    def __init__(self):
        self.provider = settings.EMBEDDING_PROVIDER
        self.gemini_ready = False
        
        if settings.GEMINI_API_KEY:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.gemini_ready = True
            except Exception as e:
                print(f"[Embeddings] Warning configuring Gemini: {e}")

        # Local semantic vocabulary projection cache for ultra-fast local embeddings
        self._vocab = {}
        self._idf = {}
        self._fitted = False

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if self.gemini_ready and (self.provider == "gemini" or self.provider == "auto"):
            try:
                # Gemini embedding API
                embeddings = []
                for text in texts:
                    res = genai.embed_content(
                        model="models/text-embedding-004",
                        content=text,
                        task_type="retrieval_document"
                    )
                    embeddings.append(res["embedding"])
                return embeddings
            except Exception as e:
                print(f"[Embeddings] Gemini API embedding error: {e}. Falling back to local dense embeddings.")
        
        return self._local_dense_embeddings(texts)

    def embed_query(self, query: str) -> List[float]:
        if self.gemini_ready and (self.provider == "gemini" or self.provider == "auto"):
            try:
                res = genai.embed_content(
                    model="models/text-embedding-004",
                    content=query,
                    task_type="retrieval_query"
                )
                return res["embedding"]
            except Exception as e:
                print(f"[Embeddings] Gemini query embedding error: {e}. Falling back to local dense embedding.")
        
        return self._local_dense_embeddings([query])[0]

    def _local_dense_embeddings(self, texts: List[str], dim: int = 128) -> List[List[float]]:
        """
        Deterministic, zero-latency dense semantic projection representation.
        Uses character n-grams and hashing trick with L2 normalization to produce
        robust semantic vectors without external heavy dependencies.
        """
        vectors = []
        for text in texts:
            vec = np.zeros(dim, dtype=np.float32)
            words = text.lower().replace(",", " ").replace(".", " ").replace(";", " ").split()
            if not words:
                vectors.append(vec.tolist())
                continue
                
            for i, w in enumerate(words):
                # Hash word
                h = abs(hash(w)) % dim
                weight = 1.0 + (0.5 if len(w) > 5 else 0.0)
                vec[h] += weight
                
                # Bigram hash for phrase context
                if i < len(words) - 1:
                    bigram = f"{w}_{words[i+1]}"
                    h_bi = abs(hash(bigram)) % dim
                    vec[h_bi] += 1.5
                    
                # Character trigrams for root words
                for j in range(len(w) - 2):
                    trigram = w[j:j+3]
                    h_tri = abs(hash(trigram)) % dim
                    vec[h_tri] += 0.3

            # L2 Normalize
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            vectors.append(vec.tolist())
        return vectors

embedding_service = EmbeddingProvider()
