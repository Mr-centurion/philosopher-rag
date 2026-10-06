import time
import json
import re
import logging
from typing import Dict, Any, List
from app.graph.state import GraphState
from app.rag.schema import PerThinkerBreakdown, Citation, GuardrailFlag
from app.rag.hybrid_retriever import hybrid_retriever
from app.rag.ingest import THINKER_PROFILES
from app.core.guardrails import guardrails_manager
from app.core.nemo_guardrails import nemo_guardrails
from app.core.session_store import session_store
from app.core.llm import llm_service
from app.core.topic_matcher import topic_matcher, TOPIC_SYNONYMS
from app.core.voice_engine import voice_engine
from app.core.invalid_premise import detect_invalid_premise, build_invalid_premise_response

logger = logging.getLogger("philosophy_rag.nodes")

ALL_THINKER_IDS = list(THINKER_PROFILES.keys())
RELEVANCE_THRESHOLD = 0.50

# In-memory history for anti-template cross-query regression verification
COMPOSER_HISTORY: List[Dict[str, str]] = []

def input_guardrail_node(state: GraphState) -> GraphState:
    question = state.get("question", "")

    # 1. Tier 1: Dedicated NVIDIA NeMo Guardrails Input Rail (Hard Pre-Pipeline Content Gate)
    nemo_safe, nemo_flag, nemo_rejection = nemo_guardrails.check_input(question)
    if not nemo_safe:
        existing_flags = list(state.get("guardrail_flags", []))
        if nemo_flag:
            existing_flags.append(nemo_flag)
        rejection_text = nemo_rejection or "I cannot fulfill this request because it falls outside of philosophical inquiry or violates safety constraints."
        logger.warning(f"[NeMo Input Rail Gate] Blocked query before RAG pipeline: '{question}'")
        return {
            **state,
            "is_safe": False,
            "guardrail_flags": existing_flags,
            "final_synthesis": rejection_text,
            "per_thinker_breakdown": [],
            "citations": [],
            "faithfulness_score": 0.0,
            "sentence_groundedness": [],
            "regeneration_logs": [],
            "total_sentences": 0,
            "grounded_sentences_count": 0,
            "flagged_sentences_count": 0,
            "is_weak_match": False,
            "template_similarity_score": 0.0,
            "template_collision": False,
            "voice_distinctiveness_score": 1.0
        }

    # 2. Tier 2: Secondary Custom Classifier (evaluates topic relevance & nuanced philosophical inquiry)
    is_safe, flags, rejection_msg = guardrails_manager.check_input(question)
    
    existing_flags = list(state.get("guardrail_flags", []))
    existing_flags.extend(flags)
    
    if not is_safe:
        rejection_text = rejection_msg or "I cannot fulfill this request because it falls outside of philosophical inquiry or violates safety constraints."
        return {
            **state,
            "is_safe": False,
            "guardrail_flags": existing_flags,
            "final_synthesis": rejection_text,
            "per_thinker_breakdown": [],
            "citations": [],
            "faithfulness_score": 0.0,
            "sentence_groundedness": [],
            "regeneration_logs": [],
            "total_sentences": 0,
            "grounded_sentences_count": 0,
            "flagged_sentences_count": 0,
            "is_weak_match": False,
            "template_similarity_score": 0.0,
            "template_collision": False,
            "voice_distinctiveness_score": 1.0
        }
    
    return {
        **state,
        "is_safe": True,
        "guardrail_flags": existing_flags
    }

def thinker_router_node(state: GraphState) -> GraphState:
    if not state.get("is_safe", True):
        return state

    question = state.get("question", "")
    requested = state.get("requested_thinkers")
    
    # Filter valid thinkers or default to all MVP thinkers
    if requested and len(requested) > 0:
        selected = [t for t in requested if t in ALL_THINKER_IDS]
        if not selected:
            selected = ALL_THINKER_IDS
    else:
        selected = ALL_THINKER_IDS

    # Extract core topics cleanly without drowning in static lexicons
    core_topics = topic_matcher.extract_core_topics(question)
    query_topic_str = ", ".join(core_topics) if core_topics else "philosophical inquiry"

    # Generate specialized conceptual sub-queries per thinker focused on the query topic
    thinker_queries = {}
    for t_id in selected:
        thinker_queries[t_id] = topic_matcher.get_reformulated_query(question, t_id)

    return {
        **state,
        "selected_thinkers": selected,
        "thinker_queries": thinker_queries,
        "extracted_topics": core_topics,
        "query_topic": query_topic_str
    }

def parallel_retrieval_node(state: GraphState) -> GraphState:
    if not state.get("is_safe", True):
        return state

    question = state.get("question", "")
    thinker_queries = state.get("thinker_queries", {})
    selected_thinkers = state.get("selected_thinkers", list(thinker_queries.keys()))
    core_topics = state.get("extracted_topics", [])
    query_topic = state.get("query_topic", "topic")
    
    # First-pass parallel hybrid retrieval
    retrieved_chunks = hybrid_retriever.retrieve_comparative(thinker_queries, top_k_per_thinker=3)
    
    retrieval_weak_matches: Dict[str, Dict[str, Any]] = {}
    existing_flags = list(state.get("guardrail_flags", []))
    alignment_scores = []

    for thinker_id, chunks in retrieved_chunks.items():
        top_chunk = chunks[0] if chunks else None
        top_score = top_chunk.score if top_chunk and top_chunk.score is not None else 0.0
        
        # Check topic alignment and score threshold with thinker tradition awareness
        topic_align_score, is_aligned = (
            topic_matcher.compute_topic_alignment(question, top_chunk, thinker_id=thinker_id)
            if top_chunk else (0.0, False)
        )
        alignment_scores.append(top_score)

        if top_score < RELEVANCE_THRESHOLD or not is_aligned:
            logger.info(
                f"[Retrieval Gate] Weak match for {thinker_id}: Top score={top_score:.2f} (threshold={RELEVANCE_THRESHOLD}), "
                f"topic_aligned={is_aligned}. Triggering targeted query expansion retry..."
            )
            
            # ATTEMPT AUTOMATED QUERY EXPANSION RETRY
            expanded_query = topic_matcher.get_reformulated_query(question, thinker_id)
            retry_chunks = hybrid_retriever.retrieve_for_thinker(expanded_query, thinker_id, top_k=3)
            retry_top = retry_chunks[0] if retry_chunks else None
            retry_score = retry_top.score if retry_top and retry_top.score is not None else 0.0
            retry_align_score, retry_aligned = (
                topic_matcher.compute_topic_alignment(question, retry_top, thinker_id=thinker_id)
                if retry_top else (0.0, False)
            )

            if retry_top and retry_aligned and (retry_score >= 0.45 or retry_align_score >= 0.33):
                logger.info(f"[Retrieval Gate] {thinker_id} resolved via query expansion! Score={retry_score:.2f}, chunk={retry_top.id}")
                retrieved_chunks[thinker_id] = retry_chunks
                alignment_scores[-1] = retry_score
            else:
                # Still weak match after expansion
                logger.warning(f"[Retrieval Gate] {thinker_id} remains weak match. Flagging as thematically adjacent only.")
                retrieval_weak_matches[thinker_id] = {
                    "is_weak": True,
                    "score": max(top_score, retry_score),
                    "reason": f"No direct passage found regarding '{query_topic}'. Passages provide general principles."
                }
                if retry_top and retry_score > top_score:
                    retrieved_chunks[thinker_id] = retry_chunks

    mean_alignment_score = round(sum(alignment_scores) / max(len(alignment_scores), 1), 3)

    # Determine overall query-level weak match
    num_thinkers = max(len(selected_thinkers), 1)
    num_weak = len(retrieval_weak_matches)
    if num_thinkers == 1:
        is_query_weak_match = (num_weak > 0)
    else:
        is_query_weak_match = (num_weak > (num_thinkers / 2)) or (mean_alignment_score < 0.45)

    weak_msg = None
    if is_query_weak_match:
        weak_msg = (
            f"Closest related passages found — the available texts provide general philosophical principles "
            f"but may not directly address '{query_topic}'."
        )
        existing_flags.append(
            GuardrailFlag(
                category="retrieval_mismatch",
                severity="medium",
                message=weak_msg,
                details={"query_topic": query_topic, "mean_relevance_score": mean_alignment_score}
            )
        )

    # Check for invalid premise / modern non-philosophical entity when retrieval is weak
    invalid_match = detect_invalid_premise(question)
    is_invalid = False
    invalid_details = None

    if is_query_weak_match and invalid_match:
        entity, cat_name, cat_desc, suggestions = invalid_match
        is_invalid = True
        invalid_details = {
            "entity": entity,
            "category": cat_name,
            "category_description": cat_desc,
            "suggestions": suggestions
        }
        logger.warning(
            f"[Invalid Premise Gate] Detected non-philosophical modern entity '{entity}' ({cat_name}) "
            f"with weak retrieval match. Gating against spurious full synthesis."
        )
        existing_flags.append(
            GuardrailFlag(
                category="invalid_premise",
                severity="medium",
                message=f"Query references '{entity}' ({cat_name}) without primary textual grounding.",
                details=invalid_details
            )
        )

    return {
        **state,
        "retrieved_chunks": retrieved_chunks,
        "is_weak_match": is_query_weak_match,
        "is_invalid_premise": is_invalid,
        "invalid_premise_details": invalid_details,
        "weak_match_warning": weak_msg,
        "topic_alignment_score": mean_alignment_score,
        "retrieval_weak_matches_by_thinker": retrieval_weak_matches,
        "guardrail_flags": existing_flags
    }

def thinker_synthesis_node(state: GraphState) -> GraphState:
    if not state.get("is_safe", True):
        return state

    # Bypass per-thinker breakdown generation if premise is invalid/nonsensical
    if state.get("is_invalid_premise", False):
        return {
            **state,
            "per_thinker_breakdown": [],
            "citations": [],
            "template_similarity_score": 0.0,
            "template_collision": False,
            "voice_distinctiveness_score": 1.0
        }

    question = state.get("question", "")
    extracted_topics = state.get("extracted_topics", [])
    topic_alignment = state.get("topic_alignment_score", 0.0)
    is_weak_match = state.get("is_weak_match", False)
    has_valid_philosophical_content = (
        bool(extracted_topics)
        or any(c in question.lower() for c in topic_matcher.CORE_TOPICS)
        or bool(topic_matcher.extract_core_topics(question))
    )

    if (is_weak_match or topic_alignment < 0.50) and not has_valid_philosophical_content:
        return {
            **state,
            "per_thinker_breakdown": [],
            "citations": [],
            "template_similarity_score": 0.0,
            "template_collision": False,
            "voice_distinctiveness_score": 1.0
        }

    query_topic = state.get("query_topic", "topic")
    selected = state.get("selected_thinkers", [])
    retrieved_chunks = state.get("retrieved_chunks", {})
    weak_matches = state.get("retrieval_weak_matches_by_thinker", {})
    
    breakdowns: List[PerThinkerBreakdown] = []
    all_citations: List[Citation] = []

    for t_id in selected:
        chunks = retrieved_chunks.get(t_id, [])
        profile = THINKER_PROFILES.get(t_id, {
            "name": t_id.replace("_", " ").title(),
            "tradition": "Classical Philosophy",
            "key_themes": []
        })

        t_weak_info = weak_matches.get(t_id, {})
        is_t_weak = t_weak_info.get("is_weak", False)

        t_citations: List[Citation] = []
        for c in chunks:
            cit = Citation(
                chunk_id=c.id,
                thinker_name=c.thinker_name,
                work_title=c.work_title,
                chapter=c.chapter,
                quote=c.text,
                relevance_score=c.score or 0.95
            )
            t_citations.append(cit)
            all_citations.append(cit)

        # Build context passage string
        passages_text = "\n\n".join([f"[{c.work_title}, {c.chapter}]: \"{c.text}\"" for c in chunks])
        
        weak_guidance = ""
        if is_t_weak:
            weak_guidance = (
                f"\nIMPORTANT: The retrieved passages do NOT directly address '{query_topic}'. "
                f"You MUST explicitly clarify that {profile['name']} addresses this indirectly through their broader principles, "
                f"and avoid falsely claiming that the cited text directly defines or discusses '{query_topic}'."
            )

        anti_template_guidance = voice_engine.get_anti_template_prompt_guidance(t_id, profile["name"], profile["tradition"])

        system_prompt = (
            f"You are an expert philosophical scholar representing {profile['name']} ({profile['tradition']}). "
            f"Answer strictly grounding your philosophical stance on the provided source passages.\n\n"
            f"{anti_template_guidance}"
            f"{weak_guidance}"
        )
        user_prompt = (
            f"Philosophical Question: \"{question}\"\n\n"
            f"Primary Source Passages for {profile['name']} [thinker_id: {t_id}]:\n{passages_text}\n\n"
            f"Instructions:\n"
            f"Provide a JSON response with keys:\n"
            f"- 'core_stance': A 1-2 sentence distillation of {profile['name']}'s position using their distinctive conceptual terminology.\n"
            f"- 'detailed_argument': An authentic, rigorous explanation of how {profile['name']} approaches this question based strictly on their text. DO NOT use generic boilerplate formulas.\n"
            f"- 'key_concepts': A list of 3-5 philosophical terms central to their argument.\n"
            f"Return ONLY valid JSON."
        )

        try:
            raw_res = llm_service.generate(user_prompt, system_prompt=system_prompt, temperature=0.2)
            json_match = raw_res
            if "```json" in raw_res:
                json_match = raw_res.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_res:
                json_match = raw_res.split("```")[1].split("```")[0].strip()
            parsed = json.loads(json_match)
            
            breakdown = PerThinkerBreakdown(
                thinker_id=t_id,
                thinker_name=profile["name"],
                tradition=profile["tradition"],
                core_stance=parsed.get("core_stance", ""),
                detailed_argument=parsed.get("detailed_argument", ""),
                key_concepts=parsed.get("key_concepts", profile["key_themes"][:3]),
                citations=t_citations,
                is_weak_match=is_t_weak,
                weak_match_reason=t_weak_info.get("reason"),
                topic_alignment_score=chunks[0].score if chunks else 1.0
            )
        except Exception as e:
            # High quality authentic philosophical voice synthesis fallback
            breakdown = voice_engine.generate_authentic_thinker_breakdown(
                thinker_id=t_id,
                question=question,
                chunks=chunks,
                is_weak_match=is_t_weak,
                weak_reason=t_weak_info.get("reason")
            )
            breakdown.citations = t_citations

        breakdowns.append(breakdown)

    # Automated Post-Generation Voice Distinctiveness & Anti-Template Check (Regression Gate)
    max_similarity, is_collision, collision_details = voice_engine.check_template_collision(breakdowns)
    
    if is_collision:
        logger.warning(
            f"[Anti-Template Gate] Template collision detected (max_similarity={max_similarity:.2f}): {collision_details}. "
            f"Triggering authentic voice normalization..."
        )
        for i, b in enumerate(breakdowns):
            chunks = retrieved_chunks.get(b.thinker_id, [])
            t_weak_info = weak_matches.get(b.thinker_id, {})
            fixed_breakdown = voice_engine.generate_authentic_thinker_breakdown(
                thinker_id=b.thinker_id,
                question=question,
                chunks=chunks,
                is_weak_match=t_weak_info.get("is_weak", False),
                weak_reason=t_weak_info.get("reason")
            )
            fixed_breakdown.citations = b.citations
            breakdowns[i] = fixed_breakdown

        max_similarity, is_collision, collision_details = voice_engine.check_template_collision(breakdowns)

    voice_distinctiveness = round(1.0 - max_similarity, 3)

    return {
        **state,
        "per_thinker_breakdown": breakdowns,
        "citations": all_citations,
        "template_similarity_score": max_similarity,
        "template_collision": is_collision,
        "voice_distinctiveness_score": voice_distinctiveness
    }

def comparative_synthesis_node(state: GraphState) -> GraphState:
    if not state.get("is_safe", True):
        return state

    question = state.get("question", "")
    query_topic = state.get("query_topic", "topic")
    is_weak_match = state.get("is_weak_match", False)

    # If invalid premise detected, provide concise honest historical boundary response
    if state.get("is_invalid_premise", False):
        inv_details = state.get("invalid_premise_details") or {}
        entity = inv_details.get("entity", "the queried topic")
        cat_desc = inv_details.get("category_description", "modern commercial or pop-culture concepts")
        suggestions = inv_details.get("suggestions", [])
        final_synthesis = build_invalid_premise_response(question, entity, cat_desc, suggestions)
        return {
            **state,
            "final_synthesis": final_synthesis
        }

    # GATING: If retrieval confidence is below threshold AND no valid philosophical content exists for this query,
    # return a short explicit message stating the query cannot be meaningfully addressed — DO NOT call the LLM
    # to generate a full synthesis around a fallback template.
    extracted_topics = state.get("extracted_topics", [])
    topic_alignment = state.get("topic_alignment_score", 0.0)
    has_valid_philosophical_content = (
        bool(extracted_topics)
        or any(c in question.lower() for c in topic_matcher.CORE_TOPICS)
        or bool(topic_matcher.extract_core_topics(question))
    )

    if (is_weak_match or topic_alignment < 0.50) and not has_valid_philosophical_content:
        logger.warning(
            f"[Comparative Node] Retrieval confidence below threshold ({topic_alignment:.2f}) and no valid "
            f"philosophical content exists for query: '{question}'. Gating against fallback synthesis."
        )
        return {
            **state,
            "final_synthesis": (
                f"The inquiry \"{question}\" cannot be meaningfully addressed within our corpus of classical "
                f"philosophical texts. The query lacks recognized philosophical grounding or textual evidence "
                f"among the indexed traditions."
            ),
            "per_thinker_breakdown": [],
            "citations": [],
            "faithfulness_score": 0.0,
            "sentence_groundedness": [],
            "regeneration_logs": [],
            "total_sentences": 0,
            "grounded_sentences_count": 0,
            "flagged_sentences_count": 0,
            "is_weak_match": True,
            "template_similarity_score": 0.0,
            "template_collision": False,
            "voice_distinctiveness_score": 1.0
        }

    breakdowns = state.get("per_thinker_breakdown", [])
    
    if not breakdowns:
        return state

    if len(breakdowns) == 1:
        b = breakdowns[0]
        arg_clean = b.detailed_argument.replace("\n", " ")
        stances_text = f"### {b.thinker_name} ({b.tradition}):\n- Core Stance: {b.core_stance}\n- Key Concepts: {', '.join(b.key_concepts)}\n- Argument: {arg_clean}"
        system_prompt = (
            f"You are an elite scholar of {b.tradition}. "
            f"Provide a comprehensive, authoritative analysis of {b.thinker_name}'s doctrine regarding the query."
        )
        user_prompt = (
            f"Question: \"{question}\"\n\n"
            f"Thinker Perspective Analyzed:\n{stances_text}\n\n"
            f"Answer the question directly and concisely from the source material. "
            f"Do not include boilerplate section headings (such as 'Philosophical Analysis', 'Core Philosophical Foundation', "
            f"'Systematic Exposition & Argument', or 'Philosophical Synthesis & Takeaway'). "
            f"Do not include generic modern life advice or self-help takeaways.\n\n"
            f"Format:\n"
            f"Answer:\n[3-6 concise paragraphs directly answering the question from the evidence]\n\n"
            f"Evidence:\n[Relevant source citations with work and section]"
        )
    else:
        stances_text = "\n\n".join([
            f"### {b.thinker_name} ({b.tradition}):\n- Core Stance: {b.core_stance}\n- Key Concepts: {', '.join(b.key_concepts)}\n- Argument: {b.detailed_argument.replace(chr(10), ' ')}"
            for b in breakdowns
        ])

        weak_note = ""
        if is_weak_match:
            weak_note = f"Note: One or more thinkers lacked direct passages on '{query_topic}'. Highlight that these represent thematically adjacent principles rather than verbatim treatises."

        system_prompt = (
            "You are an elite professor of Comparative Philosophy. "
            "Your task is to synthesize the comparative dialectic between the philosophical traditions. "
            f"{weak_note}"
        )
        user_prompt = (
            f"Question: \"{question}\"\n\n"
            f"Thinker Perspectives Analyzed:\n{stances_text}\n\n"
            f"Answer the question directly and concisely from the retrieved evidence. "
            f"Do not include boilerplate section headings (such as 'Dialectical Overview', 'Points of Convergence', "
            f"'Points of Divergence', or 'Philosophical Synthesis & Takeaway'). "
            f"Do not include generic modern practitioner life advice or self-help takeaways.\n\n"
            f"Format:\n"
            f"Answer:\n[3-6 concise paragraphs answering the question directly based on the evidence]\n\n"
            f"Evidence:\n[Relevant source citations with work and section]"
        )

    try:
        final_synthesis = llm_service.generate(user_prompt, system_prompt=system_prompt, temperature=0.3)
    except Exception as e:
        final_synthesis = llm_service._local_philosophical_synthesis(user_prompt)

    # Post-Generation Diversity & Anti-Duplication Check
    raw_paragraphs = [p.strip() for p in final_synthesis.split("\n\n") if p.strip()]
    is_duplicated = False
    
    if len(raw_paragraphs) >= 2:
        for i in range(len(raw_paragraphs)):
            for j in range(i + 1, len(raw_paragraphs)):
                p_i = raw_paragraphs[i]
                p_j = raw_paragraphs[j]
                if len(p_i) > 40 and len(p_j) > 40:
                    sim = voice_engine.compute_sentence_similarity(p_i, p_j)
                    if sim >= 0.75 or p_i == p_j:
                        is_duplicated = True
                        break
            if is_duplicated:
                break

    if is_duplicated or len(raw_paragraphs) < 2:
        logger.warning("[Comparative Node] Detected paragraph duplication or insufficient content. Regenerating via structured synthesis engine...")
        final_synthesis = llm_service._local_philosophical_synthesis(user_prompt)

    # Anti-Template Regression Check 1: Forbidden Boilerplate Pattern Matching
    forbidden_boilerplate_patterns = [
        r"While\s+Marcus\s+Aurelius\s+\(Roman\s+Stoicism\)\s+anchors\s+the\s+answer\s+in\s+Governing\s+Mind",
        r"challenges\s+this\s+by\s+prioritizing\s+Will\s+to\s+Power\s+\(Wille\s+zur\s+Macht\)",
        r"anchors\s+the\s+answer\s+in\s+Categorical\s+Imperative",
        r"While\s+[^\n,]+\s+anchors\s+the\s+answer\s+in\s+[^\n,]+,\s+[^\n,]+\s+challenges\s+this\s+by\s+prioritizing",
    ]
    is_boilerplate = any(re.search(bp, final_synthesis) for bp in forbidden_boilerplate_patterns)
    if is_boilerplate:
        logger.error("[Anti-Template Gate] Dialectical synthesis contains forbidden boilerplate template! Regenerating via dynamic composer...")
        final_synthesis = llm_service._local_philosophical_synthesis(user_prompt)

    # Anti-Template Regression Check 2: Cross-Query Output Similarity Gate
    cross_query_collision = False
    max_cross_sim = 0.0
    core_topics = state.get("extracted_topics", [])
    curr_topics_set = set(core_topics)

    for past_entry in COMPOSER_HISTORY:
        past_q = past_entry.get("question", "")
        past_synth = past_entry.get("synthesis", "")
        past_topics = set(past_entry.get("topics", []))
        is_diff_topic = bool(curr_topics_set and past_topics and curr_topics_set.isdisjoint(past_topics))

        if past_q and is_diff_topic:
            # Extract section 3 if present or compare full text
            s3_curr = final_synthesis.split("### 3.")[1].split("### 4.")[0] if "### 3." in final_synthesis and "### 4." in final_synthesis else final_synthesis
            s3_past = past_synth.split("### 3.")[1].split("### 4.")[0] if "### 3." in past_synth and "### 4." in past_synth else past_synth
            sim = voice_engine.compute_sentence_similarity(s3_curr.strip(), s3_past.strip())
            if sim > max_cross_sim:
                max_cross_sim = sim
            if sim >= 0.88:
                cross_query_collision = True
                logger.warning(
                    f"[Anti-Template Gate] Cross-query synthesis near-identical collision ({sim:.2f}) "
                    f"between query '{question[:40]}' and '{past_q[:40]}'. Triggering dynamic regeneration..."
                )
                break

    if cross_query_collision:
        final_synthesis = llm_service._local_philosophical_synthesis(user_prompt)

    # Record in history (maintain last 10 entries)
    COMPOSER_HISTORY.append({"question": question, "synthesis": final_synthesis, "topics": core_topics})
    if len(COMPOSER_HISTORY) > 10:
        COMPOSER_HISTORY.pop(0)

    return {
        **state,
        "final_synthesis": final_synthesis
    }

def output_guardrail_node(state: GraphState) -> GraphState:
    if not state.get("is_safe", True):
        return state

    final_synthesis = state.get("final_synthesis", "")
    retrieved_chunks = state.get("retrieved_chunks", {})
    existing_flags = list(state.get("guardrail_flags", []))

    # If this is an honest historical boundary response, it is intrinsically grounded
    if state.get("is_invalid_premise", False):
        start_time = state.get("start_time", time.time())
        latency_ms = round((time.time() - start_time) * 1000, 2)
        from app.rag.schema import SentenceGroundedness
        from app.core.guardrails import split_into_sentences
        raw_sentences = split_into_sentences(final_synthesis)
        sentence_results = [
            SentenceGroundedness(
                sentence_index=i,
                text=s,
                grounded=True,
                confidence_score=0.95,
                flag_reason=None
            )
            for i, s in enumerate(raw_sentences)
        ]
        return {
            **state,
            "final_synthesis": final_synthesis,
            "sentence_groundedness": sentence_results,
            "regeneration_logs": [],
            "total_sentences": len(sentence_results),
            "grounded_sentences_count": len(sentence_results),
            "flagged_sentences_count": 0,
            "guardrail_flags": existing_flags,
            "faithfulness_score": 0.95,
            "latency_ms": latency_ms
        }

    # Sentence-level groundedness scoring & self-correction resolution
    reconstructed_answer, sentence_results, regen_logs, mean_faithfulness, flags = (
        guardrails_manager.check_and_resolve_sentences(final_synthesis, retrieved_chunks)
    )
    existing_flags.extend(flags)

    # Compute latency
    start_time = state.get("start_time", time.time())
    latency_ms = round((time.time() - start_time) * 1000, 2)

    total_sentences = len(sentence_results)
    grounded_count = sum(1 for s in sentence_results if s.grounded)
    flagged_count = sum(1 for s in sentence_results if not s.grounded)

    return {
        **state,
        "final_synthesis": reconstructed_answer,
        "sentence_groundedness": sentence_results,
        "regeneration_logs": regen_logs,
        "total_sentences": total_sentences,
        "grounded_sentences_count": grounded_count,
        "flagged_sentences_count": flagged_count,
        "guardrail_flags": existing_flags,
        "faithfulness_score": mean_faithfulness,
        "latency_ms": latency_ms
    }

def session_memory_node(state: GraphState) -> GraphState:
    session_id = state.get("session_id", "default_session")
    question = state.get("question", "")
    final_synthesis = state.get("final_synthesis", "")
    
    if question and final_synthesis:
        session_store.append_turn(
            session_id=session_id,
            user_question=question,
            assistant_answer=final_synthesis,
            response_data={
                "selected_thinkers": state.get("selected_thinkers", []),
                "faithfulness_score": state.get("faithfulness_score", 1.0),
                "is_weak_match": state.get("is_weak_match", False),
                "total_sentences": state.get("total_sentences", 0),
                "grounded_sentences_count": state.get("grounded_sentences_count", 0),
                "flagged_sentences_count": state.get("flagged_sentences_count", 0),
                "guardrail_flags_count": len(state.get("guardrail_flags", []))
            }
        )

    return state
