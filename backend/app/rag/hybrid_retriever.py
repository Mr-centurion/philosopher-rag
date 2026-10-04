from typing import List, Dict, Optional, Tuple
from app.rag.schema import Chunk, Citation
from app.rag.vector_store import vector_store
from app.rag.bm25_index import bm25_manager
from app.rag.reranker import reranker_service
from app.config import settings

class HybridRetriever:
    def __init__(self, vector_weight: float = 0.55, bm25_weight: float = 0.45):
        self.vector_weight = vector_weight
        self.bm25_weight = bm25_weight
        self.rrf_k = 60

    def retrieve_for_thinker(self, query: str, thinker_id: str, top_k: int = 3) -> List[Chunk]:
        # 1. Dense Vector Search
        vector_results = vector_store.search(query, thinker_id=thinker_id, top_k=settings.VECTOR_TOP_K)
        
        # 2. Sparse BM25 Search
        bm25_results = bm25_manager.search(query, thinker_id=thinker_id, top_k=settings.BM25_TOP_K)

        # 3. Reciprocal Rank Fusion (RRF)
        fused_scores: Dict[str, float] = {}
        chunk_map: Dict[str, Chunk] = {}

        # Process Vector ranks
        for rank, (chunk, score) in enumerate(vector_results):
            chunk_map[chunk.id] = chunk
            fused_scores[chunk.id] = fused_scores.get(chunk.id, 0.0) + (self.vector_weight / (self.rrf_k + rank + 1))

        # Process BM25 ranks
        for rank, (chunk, score) in enumerate(bm25_results):
            chunk_map[chunk.id] = chunk
            fused_scores[chunk.id] = fused_scores.get(chunk.id, 0.0) + (self.bm25_weight / (self.rrf_k + rank + 1))

        # Build candidate list with initial fused score
        candidates = []
        for chunk_id, fused_score in fused_scores.items():
            c = chunk_map[chunk_id].model_copy()
            c.score = round(fused_score * 100, 4)
            c.retrieval_source = "hybrid"
            candidates.append(c)

        # 4. FlashRank / Multi-factor Reranking with Thinker Tradition Awareness
        final_chunks = reranker_service.rerank(query, candidates, thinker_id=thinker_id, top_k=top_k)
        return final_chunks

    def retrieve_comparative(self, thinker_queries: Dict[str, str], top_k_per_thinker: int = 3) -> Dict[str, List[Chunk]]:
        """
        Executes parallel / isolated hybrid retrieval for each thinker based on their specific sub-query.
        """
        results_by_thinker: Dict[str, List[Chunk]] = {}
        for thinker_id, query in thinker_queries.items():
            results_by_thinker[thinker_id] = self.retrieve_for_thinker(query, thinker_id, top_k=top_k_per_thinker)
        return results_by_thinker

hybrid_retriever = HybridRetriever()
