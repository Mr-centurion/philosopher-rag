from typing import TypedDict, List, Dict, Optional, Any
from app.rag.schema import Chunk, PerThinkerBreakdown, Citation, GuardrailFlag, SentenceGroundedness, RegenerationLog

class GraphState(TypedDict, total=False):
    question: str
    requested_thinkers: Optional[List[str]]
    selected_thinkers: List[str]
    session_id: str
    chat_history: List[Dict[str, str]]
    
    # Guardrails and routing
    is_safe: bool
    guardrail_flags: List[GuardrailFlag]
    thinker_queries: Dict[str, str]
    extracted_topics: List[str]
    
    # Retrieval outputs
    retrieved_chunks: Dict[str, List[Chunk]]
    
    # Relevance Threshold & Topic Alignment Gating
    is_weak_match: bool
    weak_match_warning: Optional[str]
    query_topic: Optional[str]
    topic_alignment_score: float
    retrieval_weak_matches_by_thinker: Dict[str, Dict[str, Any]]
    
    # Generation outputs
    per_thinker_breakdown: List[PerThinkerBreakdown]
    final_synthesis: str
    citations: List[Citation]
    
    # Granular Sentence-Level Groundedness & Self-Correction
    sentence_groundedness: List[SentenceGroundedness]
    regeneration_logs: List[RegenerationLog]
    total_sentences: int
    grounded_sentences_count: int
    flagged_sentences_count: int

    # Voice Distinctiveness & Anti-Templating
    template_similarity_score: float
    template_collision: bool
    voice_distinctiveness_score: float

    # Evaluation / Metrics
    faithfulness_score: float
    start_time: float
    latency_ms: float
