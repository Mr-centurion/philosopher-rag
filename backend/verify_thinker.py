import asyncio
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app.rag.hybrid_retriever import hybrid_retriever
from app.graph.workflow import run_query_workflow
from app.rag.bm25_index import bm25_manager
from app.rag.vector_store import vector_store

async def verify_thinker(thinker_id: str, query: str):
    print("=" * 80)
    print(f"VERIFICATION REPORT FOR THINKER: {thinker_id.upper()}")
    print("=" * 80)

    # 1. Namespace Isolation Check
    print("\n--- 1. NAMESPACE ISOLATION TEST ---")
    retrieved_chunks = hybrid_retriever.retrieve_for_thinker(query, thinker_id, top_k=5)
    foreign_chunks = [c for c in retrieved_chunks if c.thinker_id != thinker_id]
    
    print(f"Total retrieved chunks: {len(retrieved_chunks)}")
    for c in retrieved_chunks:
        print(f"  Chunk ID: {c.id} | Thinker: {c.thinker_id} ({c.thinker_name}) | Work: {c.work_title}")
    
    if foreign_chunks:
        print(f"❌ ISOLATION BREACH DETECTED: {len(foreign_chunks)} foreign chunks found!")
        for fc in foreign_chunks:
            print(f"  BREACH: {fc.id} belongs to {fc.thinker_id}")
    else:
        print(f"✅ NAMESPACE ISOLATION CONFIRMED: 100% of retrieved chunks belong strictly to '{thinker_id}'.")

    # Also verify that a query for another thinker does NOT retrieve this thinker
    test_other_id = "marcus_aurelius" if thinker_id != "marcus_aurelius" else "friedrich_nietzsche"
    other_chunks = hybrid_retriever.retrieve_for_thinker(query, test_other_id, top_k=5)
    leaked_into_other = [c for c in other_chunks if c.thinker_id == thinker_id]
    if leaked_into_other:
        print(f"❌ CROSS-CONTAMINATION: {thinker_id} chunks leaked into {test_other_id}'s search!")
    else:
        print(f"✅ REVERSE ISOLATION CONFIRMED: Zero {thinker_id} chunks leaked into {test_other_id}'s search space.")

    # 2. Single-Thinker Retrieval Detail (Top Chunks, Scores, Excerpts)
    print("\n--- 2. RETRIEVAL VERIFICATION (TOP CHUNKS & RERANK SCORES) ---")
    for idx, c in enumerate(retrieved_chunks[:3], 1):
        print(f"\n[Rank {idx}] Chunk ID: {c.id}")
        print(f"Title / Chapter: {c.work_title} — {c.chapter}")
        print(f"Raw Rerank Score: {c.score}")
        print(f"Text Excerpt: \"{c.text[:220]}...\"")

    # 3. Voice Distinctiveness & End-to-End Workflow Verification
    print("\n--- 3. VOICE DISTINCTIVENESS & SYNTHESIS CHECK ---")
    response = await run_query_workflow(query, requested_thinkers=[thinker_id], session_id=f"verify_{thinker_id}")
    
    print(f"Faithfulness Score: {response.faithfulness_score}")
    print(f"Voice Distinctiveness Score: {response.voice_distinctiveness_score}")
    print(f"Template Collision Detected: {response.template_collision}")
    
    for b in response.per_thinker_breakdown:
        print(f"\n[Thinker Breakdown: {b.thinker_name} ({b.tradition})]")
        print(f"Core Stance:\n  {b.core_stance}")
        print(f"\nDetailed Argument Excerpt:\n  {b.detailed_argument[:300]}...")
        print(f"\nKey Concepts: {', '.join(b.key_concepts)}")
        
        # Check against generic boilerplate
        generic_markers = [
            "emphasizing rational agency",
            "aligning conscious judgment",
            "unshakeable integrity",
            "grounds their position directly in primary source doctrines"
        ]
        has_generic = any(m in b.detailed_argument.lower() or m in b.core_stance.lower() for m in generic_markers)
        if has_generic:
            print("❌ WARNING: Generic boilerplate phrase detected in breakdown!")
        else:
            print("✅ DISTINCT VOICE CONFIRMED: No generic boilerplate language detected.")

if __name__ == "__main__":
    t_id = sys.argv[1] if len(sys.argv) > 1 else "seneca"
    q = sys.argv[2] if len(sys.argv) > 2 else "What does Seneca say about the shortage of time and how mortals waste their lives in Letters to Lucilius?"
    asyncio.run(verify_thinker(t_id, q))
