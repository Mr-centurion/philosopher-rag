import json
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any
from app.config import settings
from app.graph.workflow import run_query_workflow
from app.rag.schema import EvaluationSummary, EvaluationItem

class Evaluator:
    def __init__(self):
        self.dataset_path = Path(settings.EVAL_DATASET_PATH)

    def load_dataset(self) -> List[Dict[str, Any]]:
        if not self.dataset_path.exists():
            return []
        with open(self.dataset_path, "r", encoding="utf-8") as f:
            return json.load(f)

    async def run_evaluation(self) -> EvaluationSummary:
        dataset = self.load_dataset()
        if not dataset:
            return EvaluationSummary(
                total_evaluations=0,
                mean_faithfulness=0.0,
                mean_context_recall=0.0,
                mean_comparative_balance=0.0,
                mean_latency_ms=0.0,
                total_sentences_evaluated=0,
                grounded_sentences_pct=0.0,
                regenerated_sentences_pct=0.0,
                unresolved_flagged_pct=0.0,
                retrieval_mismatches_count=0,
                retrieval_mismatch_rate_pct=0.0,
                details=[],
                timestamp=datetime.now(timezone.utc).isoformat()
            )

        items: List[EvaluationItem] = []
        total_sentences_all = 0
        total_grounded_all = 0
        total_regenerated_all = 0
        total_unresolved_all = 0
        total_retrieval_mismatches = 0
        
        for record in dataset:
            t0 = time.time()
            q_id = record.get("id", "q")
            question = record.get("question", "")
            expected_thinkers = record.get("expected_thinkers", [])
            key_terms = record.get("key_grounding_terms", [])

            # Run query through RAG workflow
            response = await run_query_workflow(
                question=question,
                requested_thinkers=expected_thinkers,
                session_id=f"eval_session_{q_id}"
            )
            elapsed_ms = (time.time() - t0) * 1000

            # 1. Faithfulness score from guardrail
            faithfulness = response.faithfulness_score

            # 2. Context Recall (check if key expected terms exist in retrieved citations)
            citation_text = " ".join([c.quote.lower() for c in response.citations])
            matched_terms = [t for t in key_terms if t.lower() in citation_text]
            context_recall = round(len(matched_terms) / max(len(key_terms), 1), 2)

            # 3. Comparative Balance Index
            represented = set([c.thinker_name.lower() for c in response.citations])
            balance = round(min(1.0, max(0.5, len(represented) / max(len(expected_thinkers), 1))), 2)

            # 4. Sentence-level metrics
            sentences = response.sentence_groundedness
            s_total = len(sentences)
            s_grounded = sum(1 for s in sentences if s.grounded and not s.was_regenerated)
            s_regenerated = sum(1 for s in sentences if s.was_regenerated and s.grounded)
            s_unresolved = sum(1 for s in sentences if not s.grounded)

            total_sentences_all += s_total
            total_grounded_all += s_grounded
            total_regenerated_all += s_regenerated
            total_unresolved_all += s_unresolved

            # 5. Distinct Retrieval Mismatch Metric
            is_mismatch = response.is_weak_match or (context_recall < 0.25 and response.topic_alignment_score < 0.50)
            if is_mismatch:
                total_retrieval_mismatches += 1

            # 6. Voice Distinctiveness & Anti-Templating
            voice_distinctiveness = response.voice_distinctiveness_score
            has_template_collision = response.template_collision

            status_val = "PASS" if (faithfulness >= 0.60 and context_recall >= 0.40 and not is_mismatch and not has_template_collision) else "WARNING"

            items.append(
                EvaluationItem(
                    query_id=q_id,
                    question=question,
                    expected_thinkers=expected_thinkers,
                    faithfulness=faithfulness,
                    context_recall=context_recall,
                    comparative_balance=balance,
                    latency_ms=round(elapsed_ms, 2),
                    status=status_val,
                    total_sentences=s_total,
                    grounded_sentences=s_grounded,
                    regenerated_sentences=s_regenerated,
                    unresolved_sentences=s_unresolved,
                    is_retrieval_mismatch=is_mismatch,
                    retrieval_topic_alignment=response.topic_alignment_score,
                    voice_distinctiveness_score=voice_distinctiveness,
                    template_collision=has_template_collision
                )
            )

        mean_faithfulness = round(sum(i.faithfulness for i in items) / len(items), 3) if items else 0.0
        mean_context_recall = round(sum(i.context_recall for i in items) / len(items), 3) if items else 0.0
        mean_comparative_balance = round(sum(i.comparative_balance for i in items) / len(items), 3) if items else 0.0
        mean_latency = round(sum(i.latency_ms for i in items) / len(items), 2) if items else 0.0

        grounded_pct = round((total_grounded_all / max(total_sentences_all, 1)) * 100, 1)
        regenerated_pct = round((total_regenerated_all / max(total_sentences_all, 1)) * 100, 1)
        unresolved_pct = round((total_unresolved_all / max(total_sentences_all, 1)) * 100, 1)
        mismatch_rate_pct = round((total_retrieval_mismatches / max(len(items), 1)) * 100, 1)

        mean_voice_distinctiveness = round(sum(i.voice_distinctiveness_score for i in items) / len(items), 3) if items else 1.0
        template_collisions_count = sum(1 for i in items if i.template_collision)
        template_collision_rate_pct = round((template_collisions_count / max(len(items), 1)) * 100, 1)

        return EvaluationSummary(
            total_evaluations=len(items),
            mean_faithfulness=mean_faithfulness,
            mean_context_recall=mean_context_recall,
            mean_comparative_balance=mean_comparative_balance,
            mean_latency_ms=mean_latency,
            total_sentences_evaluated=total_sentences_all,
            grounded_sentences_pct=grounded_pct,
            regenerated_sentences_pct=regenerated_pct,
            unresolved_flagged_pct=unresolved_pct,
            retrieval_mismatches_count=total_retrieval_mismatches,
            retrieval_mismatch_rate_pct=mismatch_rate_pct,
            mean_voice_distinctiveness_score=mean_voice_distinctiveness,
            template_collision_count=template_collisions_count,
            template_collision_rate_pct=template_collision_rate_pct,
            details=items,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

evaluator_service = Evaluator()
