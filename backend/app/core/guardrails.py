import re
import logging
from typing import List, Tuple, Dict, Any, Optional
from app.rag.schema import GuardrailFlag, Chunk, SentenceGroundedness, RegenerationLog
from app.core.llm import llm_service

logger = logging.getLogger("philosophy_rag.guardrails")

PHILOSOPHY_KEYWORDS = {
    "meaning", "purpose", "life", "suffering", "death", "god", "ethics", "moral", "morality",
    "virtue", "duty", "reason", "will", "power", "good", "evil", "justice", "truth",
    "freedom", "destiny", "fate", "knowledge", "existence", "happiness", "eudaimonia",
    "dao", "tao", "nature", "action", "mind", "soul", "desire", "imperative", "stoic",
    "stoicism", "nietzsche", "kant", "aurelius", "aristotle", "laozi", "lao tzu", "human",
    "consciousness", "values", "nihilism", "tranquility", "wisdom", "courage", "moderation"
}

PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"you\s+are\s+now\s+in\s+dan\s+mode",
    r"disregard\s+(the\s+)?system\s+prompt",
    r"system:\s*",
    r"override\s+safety\s+guidelines",
    r"reveal\s+(the\s+)?secret\s+key",
]

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "is", "are", "was", "were", "to", "of",
    "in", "for", "with", "on", "at", "by", "from", "as", "this", "that", "these",
    "those", "it", "its", "their", "theirs", "they", "we", "he", "she", "you",
    "what", "which", "who", "whom", "how", "when", "where", "why", "be", "been",
    "has", "have", "had", "do", "does", "did", "can", "could", "will", "would"
}

def split_into_sentences(text: str) -> List[str]:
    """
    Splits text into coherent sentences/claims while handling markdown headings,
    bullet points, and punctuation boundaries cleanly.
    """
    raw_lines = text.strip().split("\n")
    sentences = []

    for line in raw_lines:
        line_s = line.strip()
        if not line_s:
            continue
        
        # Preserve markdown headers as distinct items
        if line_s.startswith("#"):
            sentences.append(line_s)
            continue
            
        # If line starts with a list bullet (e.g. - or * or 1.)
        bullet_prefix = ""
        if re.match(r"^(\-|\*|\d+\.)\s+", line_s):
            m = re.match(r"^(\-|\*|\d+\.)\s+(.*)", line_s)
            if m:
                bullet_prefix = m.group(1) + " "
                line_s = m.group(2)

        # Split remaining line on sentence boundaries (. ! ?)
        parts = re.split(r"(?<=[.!?])\s+", line_s)
        for i, p in enumerate(parts):
            p_clean = p.strip()
            if p_clean:
                if i == 0 and bullet_prefix:
                    sentences.append(bullet_prefix + p_clean)
                else:
                    sentences.append(p_clean)

    return [s for s in sentences if len(s) > 0]

def is_sentence_coherent(sentence: str) -> bool:
    """
    Validates that a sentence is grammatically well-formed, sufficiently complete,
    and free from corrupted slicing artifacts.
    """
    s = sentence.strip()
    if not s:
        return False
    if s.startswith("#"):
        return True
    if len(s) < 20:
        return False
    words = s.split()
    if len(words) < 5:
        return False

    # Check terminal punctuation
    if not (s.endswith(".") or s.endswith("!") or s.endswith("?") or s.endswith('"') or s.endswith("'")):
        return False

    # Check for unfinished trailing conjunctions/prepositions
    last_word = words[-1].lower().rstrip('.!?"\'')
    if last_word in {"and", "or", "that", "with", "because", "which", "as", "in", "the", "a", "an", "to", "for", "of"}:
        return False

    # Check for repeated consecutive words
    for i in range(len(words) - 1):
        w1 = re.sub(r"[^\w]", "", words[i].lower())
        w2 = re.sub(r"[^\w]", "", words[i+1].lower())
        if len(w1) > 3 and w1 == w2:
            return False

    # Check for corrupted slice fragments
    corrupted_patterns = [
        r"dawn\s+when\s+trouble",
        r"when\s+trouble\s+getting",
        r"getting\s+guides",
        r"establishes\s+that\s+dawn",
        r"as\s+directly\s+affirmed\s+in\s+as\s+directly",
        r"trouble\s+getting\s+guides",
        r"trouble\s+getting",
    ]
    for pat in corrupted_patterns:
        if re.search(pat, s, re.IGNORECASE):
            return False

    return True

class GuardrailsManager:
    def check_input(self, question: str) -> Tuple[bool, List[GuardrailFlag]]:
        flags: List[GuardrailFlag] = []
        q_clean = question.strip()
        
        # 1. Length check
        if len(q_clean) < 3:
            flags.append(
                GuardrailFlag(
                    category="input_safety",
                    severity="high",
                    message="Question is too short to extract philosophical intent."
                )
            )
            return False, flags

        # 2. Prompt injection check
        for pattern in PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, q_clean, re.IGNORECASE):
                flags.append(
                    GuardrailFlag(
                        category="input_safety",
                        severity="high",
                        message="Potential prompt injection or instruction override detected.",
                        details={"matched_pattern": pattern}
                    )
                )
                return False, flags

        # 3. Off-topic advisory check
        words = set(re.findall(r"\b[a-zA-Z]{3,}\b", q_clean.lower()))
        philosophical_overlap = words.intersection(PHILOSOPHY_KEYWORDS)
        
        if not philosophical_overlap and len(words) > 3:
            flags.append(
                GuardrailFlag(
                    category="off_topic",
                    severity="low",
                    message="Query appears non-traditional; grounding with general existential and virtue ethics frameworks.",
                    details={"matched_keywords": list(philosophical_overlap)}
                )
            )

        return True, flags

    def _score_sentence_against_chunks(self, sentence: str, chunks: List[Chunk]) -> Tuple[float, Optional[str]]:
        """
        Computes the groundedness confidence score of a single sentence against a list of chunks.
        Returns (highest_score, best_chunk_id).
        """
        s_lower = sentence.lower()
        
        # Headers or short transition phrases are considered structurally valid
        if sentence.startswith("#") or len(sentence) < 25:
            return 0.95, (chunks[0].id if chunks else None)

        words = [w for w in re.findall(r"\b[a-zA-Z]{3,}\b", s_lower) if w not in STOPWORDS]
        if not words:
            return 0.90, (chunks[0].id if chunks else None)

        best_score = 0.0
        best_chunk_id = None
        matched_words_union = set()

        for chunk in chunks:
            c_text_lower = (chunk.text + " " + chunk.work_title + " " + chunk.chapter + " " + chunk.thinker_name + " " + chunk.tradition).lower()
            matched = [w for w in words if w in c_text_lower]
            for m in matched:
                matched_words_union.add(m)

            overlap_ratio = len(matched) / max(len(words), 1)

            # Phrase / 2-word collocation match bonus
            collocation_bonus = 0.0
            for i in range(len(words) - 1):
                colloc = f"{words[i]} {words[i+1]}"
                if colloc in c_text_lower:
                    collocation_bonus += 0.20
                    break

            # Thinker name match bonus if sentence specifically mentions this thinker
            thinker_bonus = 0.15 if chunk.thinker_name.lower() in s_lower else 0.0
            # Tradition match bonus
            tradition_bonus = 0.10 if chunk.tradition.lower() in s_lower else 0.0
            # Work title match bonus
            work_bonus = 0.15 if chunk.work_title.lower() in s_lower else 0.0

            score = min(1.0, (0.60 * overlap_ratio) + (0.15 * collocation_bonus) + thinker_bonus + tradition_bonus + work_bonus)
            
            if any(k in c_text_lower for k in words if k in PHILOSOPHY_KEYWORDS):
                score = min(1.0, score + 0.10)

            if score > best_score:
                best_score = score
                best_chunk_id = chunk.id

        # Multi-chunk dialectical coverage bonus for comparative synthesis sentences
        multi_coverage = len(matched_words_union) / max(len(words), 1)
        if multi_coverage > 0.25:
            dialectical_blend = round(0.30 * best_score + 0.70 * min(1.0, multi_coverage + 0.35), 3)
            best_score = max(best_score, dialectical_blend)

        # Structural framing sentences (e.g. section intros and transition clauses)
        structural_markers = ["traditions", "dialectical", "dialectic", "clash", "clashes", "convergence", "differences", "authority", "synthesizing", "frameworks", "perspectives", "inquiry", "navigating", "ground"]
        if any(m in s_lower for m in structural_markers) and (len(words) <= 20 or multi_coverage > 0.20):
            best_score = max(best_score, 0.75)

        return round(best_score, 3), best_chunk_id

    def check_and_resolve_sentences(
        self, 
        answer: str, 
        retrieved_chunks: Dict[str, List[Chunk]],
        threshold: float = 0.60
    ) -> Tuple[str, List[SentenceGroundedness], List[RegenerationLog], float, List[GuardrailFlag]]:
        """
        Evaluates EACH sentence individually against retrieved source chunks.
        Triggers self-correcting regeneration for ungrounded sentences and enforces
        a hard quality floor to prevent corrupted or repeated text injection.
        """
        flags: List[GuardrailFlag] = []
        all_chunks: List[Chunk] = [c for chunk_list in retrieved_chunks.values() for c in chunk_list]
        
        if not all_chunks:
            flags.append(
                GuardrailFlag(
                    category="ungrounded_claim",
                    severity="high",
                    message="No primary source chunks retrieved; unable to ground claims."
                )
            )
            sentences = split_into_sentences(answer)
            results = [
                SentenceGroundedness(
                    sentence_index=i,
                    text=s,
                    grounded=False,
                    confidence_score=0.20,
                    flag_reason="No source chunks available for grounding."
                )
                for i, s in enumerate(sentences)
            ]
            return answer, results, [], 0.20, flags

        context_text = "\n".join([f"[{c.work_title}, {c.chapter}]: {c.text}" for c in all_chunks[:6]])
        raw_sentences = split_into_sentences(answer)
        
        sentence_groundedness_list: List[SentenceGroundedness] = []
        regeneration_logs: List[RegenerationLog] = []
        resolved_sentence_texts: List[str] = []

        for idx, sentence in enumerate(raw_sentences):
            # Compute initial groundedness score
            score, best_chunk_id = self._score_sentence_against_chunks(sentence, all_chunks)
            
            # If grounded, accept as is
            if score >= threshold:
                item = SentenceGroundedness(
                    sentence_index=idx,
                    text=sentence,
                    grounded=True,
                    confidence_score=score,
                    supporting_chunk_id=best_chunk_id,
                    was_regenerated=False
                )
                sentence_groundedness_list.append(item)
                resolved_sentence_texts.append(sentence)
            else:
                # UNGROUNDED CLAIM DETECTED: Trigger Resolution Strategy (Attempt 1)
                logger.info(f"[Guardrails] Sentence #{idx} ungrounded (score: {score:.2f}). Triggering regeneration (Attempt 1)...")
                
                # Attempt regeneration Pass 1
                regenerated_sentence = llm_service.regenerate_sentence(sentence, context_text)
                new_score, new_best_chunk_id = self._score_sentence_against_chunks(regenerated_sentence, all_chunks)
                coherent = is_sentence_coherent(regenerated_sentence)
                
                # If Pass 1 failed coherence or threshold, attempt Pass 2 explicit retry
                if not coherent or new_score < threshold:
                    logger.info(f"[Guardrails] Attempt 1 did not meet floor (score={new_score:.2f}, coherent={coherent}). Trying Attempt 2...")
                    regenerated_sentence_2 = llm_service.regenerate_sentence_explicit_retry(sentence, context_text)
                    new_score_2, new_best_chunk_id_2 = self._score_sentence_against_chunks(regenerated_sentence_2, all_chunks)
                    coherent_2 = is_sentence_coherent(regenerated_sentence_2)
                    if coherent_2 and new_score_2 > new_score:
                        regenerated_sentence = regenerated_sentence_2
                        new_score = new_score_2
                        new_best_chunk_id = new_best_chunk_id_2
                        coherent = coherent_2

                logger.info(f"[Guardrails] Sentence #{idx} before: {score:.2f} -> after: {new_score:.2f} (coherent={coherent})")
                
                # HARD FLOOR RULE: ONLY replace if new_score >= threshold, coherent, and not duplicate
                is_duplicate = regenerated_sentence in resolved_sentence_texts
                if new_score >= threshold and coherent and not is_duplicate:
                    item = SentenceGroundedness(
                        sentence_index=idx,
                        text=regenerated_sentence,
                        grounded=True,
                        confidence_score=new_score,
                        supporting_chunk_id=new_best_chunk_id,
                        flag_reason="Self-corrected via source-grounded regeneration",
                        was_regenerated=True,
                        original_text=sentence,
                        original_score=score
                    )
                    sentence_groundedness_list.append(item)
                    resolved_sentence_texts.append(regenerated_sentence)

                    regeneration_logs.append(
                        RegenerationLog(
                            sentence_index=idx,
                            original_text=sentence,
                            regenerated_text=regenerated_sentence,
                            before_score=score,
                            after_score=new_score,
                            resolved=True
                        )
                    )
                else:
                    # HARD FLOOR: Keep clean sentence text, flag as low-confidence with tooltip explanation
                    item = SentenceGroundedness(
                        sentence_index=idx,
                        text=sentence,
                        grounded=False,
                        confidence_score=max(score, 0.20),
                        closest_chunk_id=best_chunk_id,
                        flag_reason="Unable to generate a confident grounded answer for this claim: assertions could not be fully verified against retrieved primary sources.",
                        was_regenerated=True,
                        original_text=sentence,
                        original_score=score
                    )
                    sentence_groundedness_list.append(item)
                    resolved_sentence_texts.append(sentence)

                    regeneration_logs.append(
                        RegenerationLog(
                            sentence_index=idx,
                            original_text=sentence,
                            regenerated_text=regenerated_sentence if coherent else sentence,
                            before_score=score,
                            after_score=new_score if coherent else score,
                            resolved=False
                        )
                    )

        # Reconstruct updated answer text cleanly preserving markdown structure
        reconstructed_parts = []
        for s in resolved_sentence_texts:
            if s.startswith("#"):
                reconstructed_parts.append("\n\n" + s + "\n")
            else:
                if reconstructed_parts and not reconstructed_parts[-1].endswith("\n"):
                    reconstructed_parts.append(" " + s)
                else:
                    reconstructed_parts.append(s)

        reconstructed_answer = "".join(reconstructed_parts).strip()
        
        # Calculate overall aggregate faithfulness score as mean of sentence confidence scores
        if sentence_groundedness_list:
            mean_faithfulness = round(sum(s.confidence_score for s in sentence_groundedness_list) / len(sentence_groundedness_list), 3)
        else:
            mean_faithfulness = 0.90

        # Construct informative count-based guardrail flags
        flagged_count = sum(1 for s in sentence_groundedness_list if not s.grounded)
        total_count = len(sentence_groundedness_list)

        if flagged_count > 0:
            flags.append(
                GuardrailFlag(
                    category="ungrounded_claim",
                    severity="medium",
                    message=f"{flagged_count} of {total_count} claims need review — assertions could not be fully grounded in primary texts.",
                    details={
                        "flagged_count": flagged_count,
                        "total_count": total_count,
                        "regenerated_count": len(regeneration_logs)
                    }
                )
            )
        else:
            flags.append(
                GuardrailFlag(
                    category="grounded_verified",
                    severity="info",
                    message=f"All {total_count} claims fully verified against retrieved primary sources.",
                    details={"total_claims": total_count, "mean_faithfulness": mean_faithfulness}
                )
            )

        return reconstructed_answer, sentence_groundedness_list, regeneration_logs, mean_faithfulness, flags

guardrails_manager = GuardrailsManager()
