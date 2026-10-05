from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ThinkerMetadata(BaseModel):
    id: str
    name: str
    tradition: str
    period: str
    avatar_url: Optional[str] = None
    color: str
    key_themes: List[str]
    sample_quote: str
    word_count: int = 0
    chunk_count: int = 0

class Chunk(BaseModel):
    id: str
    thinker_id: str
    thinker_name: str
    tradition: str
    work_title: str
    chapter: str
    text: str
    score: Optional[float] = None
    retrieval_source: Optional[str] = None  # "vector", "bm25", "hybrid"

class Citation(BaseModel):
    chunk_id: str
    thinker_name: str
    work_title: str
    chapter: str
    quote: str
    relevance_score: float = 1.0

class PerThinkerBreakdown(BaseModel):
    thinker_id: str
    thinker_name: str
    tradition: str
    core_stance: str
    detailed_argument: str
    key_concepts: List[str]
    citations: List[Citation] = Field(default_factory=list)
    is_weak_match: bool = False
    weak_match_reason: Optional[str] = None
    topic_alignment_score: float = 1.0

class GuardrailFlag(BaseModel):
    category: str  # "input_safety", "off_topic", "ungrounded_claim", "hallucination_risk", "retrieval_mismatch"
    severity: str  # "low", "medium", "high", "info"
    message: str
    details: Optional[Dict[str, Any]] = None

class SentenceGroundedness(BaseModel):
    sentence_index: int
    text: str
    grounded: bool  # True if confidence_score >= threshold
    confidence_score: float = 1.0  # 0.0 to 1.0
    supporting_chunk_id: Optional[str] = None
    closest_chunk_id: Optional[str] = None
    flag_reason: Optional[str] = None
    was_regenerated: bool = False
    original_text: Optional[str] = None
    original_score: Optional[float] = None

class RegenerationLog(BaseModel):
    sentence_index: int
    original_text: str
    regenerated_text: str
    before_score: float
    after_score: float
    resolved: bool

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=2, description="The philosophical question to analyze")
    thinkers: Optional[List[str]] = Field(default=None, description="List of thinker IDs or None for automatic comparative mode")
    session_id: str = Field(default="default_session", description="Session identifier for multi-turn history")

class QueryResponse(BaseModel):
    answer: str
    per_thinker_breakdown: List[PerThinkerBreakdown]
    citations: List[Citation]
    guardrail_flags: List[GuardrailFlag]
    faithfulness_score: float = 1.0
    latency_ms: Optional[float] = None
    selected_thinkers: List[str] = Field(default_factory=list)
    is_safe: bool = True
    
    # Granular sentence-level groundedness & self-correction
    sentence_groundedness: List[SentenceGroundedness] = Field(default_factory=list)
    regeneration_logs: List[RegenerationLog] = Field(default_factory=list)
    total_sentences: int = 0
    grounded_sentences_count: int = 0
    flagged_sentences_count: int = 0

    # Retrieval Relevance Threshold & Topic Alignment Gating
    is_weak_match: bool = False
    weak_match_warning: Optional[str] = None
    query_topic: Optional[str] = None
    topic_alignment_score: float = 1.0

    # Voice Distinctiveness & Anti-Templating
    template_similarity_score: float = 0.0
    template_collision: bool = False
    voice_distinctiveness_score: float = 1.0

class SessionMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str
    timestamp: str
    response_data: Optional[Dict[str, Any]] = None

class SessionHistoryResponse(BaseModel):
    session_id: str
    messages: List[SessionMessage]
    created_at: str
    updated_at: str

class EvaluationItem(BaseModel):
    query_id: str
    question: str
    expected_thinkers: List[str]
    faithfulness: float
    context_recall: float
    comparative_balance: float
    latency_ms: float
    status: str
    total_sentences: int = 0
    grounded_sentences: int = 0
    regenerated_sentences: int = 0
    unresolved_sentences: int = 0
    is_retrieval_mismatch: bool = False
    retrieval_topic_alignment: float = 1.0
    voice_distinctiveness_score: float = 1.0
    template_collision: bool = False

class EvaluationSummary(BaseModel):
    total_evaluations: int
    mean_faithfulness: float
    mean_context_recall: float
    mean_comparative_balance: float
    mean_latency_ms: float
    total_sentences_evaluated: int = 0
    grounded_sentences_pct: float = 0.0
    regenerated_sentences_pct: float = 0.0
    unresolved_flagged_pct: float = 0.0
    
    # Distinct retrieval failure rate
    retrieval_mismatches_count: int = 0
    retrieval_mismatch_rate_pct: float = 0.0

    # Voice distinctiveness and template collision rate
    mean_voice_distinctiveness_score: float = 1.0
    template_collision_count: int = 0
    template_collision_rate_pct: float = 0.0
    
    details: List[EvaluationItem]
    timestamp: str
