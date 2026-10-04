import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.rag.ingest import ingestion_pipeline
from app.rag.hybrid_retriever import hybrid_retriever

@pytest.fixture(autouse=True)
def setup_corpus():
    ingestion_pipeline.run()

@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["thinkers_count"] == 5

@pytest.mark.asyncio
async def test_thinkers_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/thinkers")
    assert response.status_code == 200
    thinkers = response.json()
    assert len(thinkers) == 5
    names = [t["name"] for t in thinkers]
    assert "Marcus Aurelius" in names
    assert "Friedrich Nietzsche" in names
    assert "Immanuel Kant" in names
    assert "Aristotle" in names
    assert "Laozi (Lao Tzu)" in names

@pytest.mark.asyncio
async def test_hybrid_retriever():
    chunks = hybrid_retriever.retrieve_for_thinker("What is the meaning of suffering?", "marcus_aurelius", top_k=2)
    assert len(chunks) > 0
    assert chunks[0].thinker_id == "marcus_aurelius"
    assert chunks[0].work_title == "Meditations"

@pytest.mark.asyncio
async def test_query_endpoint_and_sentence_groundedness():
    payload = {
        "question": "What is the nature of suffering and duty?",
        "thinkers": ["marcus_aurelius", "friedrich_nietzsche"],
        "session_id": "test_session_1"
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert len(data["per_thinker_breakdown"]) == 2
    assert len(data["citations"]) > 0
    assert data["faithfulness_score"] > 0
    
    # Verify sentence-level groundedness fields
    assert "sentence_groundedness" in data
    assert len(data["sentence_groundedness"]) > 0
    first_sent = data["sentence_groundedness"][0]
    assert "text" in first_sent
    assert "grounded" in first_sent
    assert "confidence_score" in first_sent
    assert data["total_sentences"] == len(data["sentence_groundedness"])
    assert data["grounded_sentences_count"] >= 0

@pytest.mark.asyncio
async def test_session_history_endpoint():
    session_id = "test_session_hist"
    payload = {
        "question": "What is virtue?",
        "thinkers": ["aristotle"],
        "session_id": session_id
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        await ac.post("/query", json=payload)
        response = await ac.get(f"/session/{session_id}/history")
    
    assert response.status_code == 200
    history = response.json()
    assert history["session_id"] == session_id
    assert len(history["messages"]) >= 2
    assert history["messages"][0]["role"] == "user"
    assert history["messages"][1]["role"] == "assistant"

@pytest.mark.asyncio
async def test_evaluate_endpoint_distribution_metrics():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/evaluate")
    assert response.status_code == 200
    summary = response.json()
    assert summary["total_evaluations"] > 0
    assert summary["mean_faithfulness"] > 0
    assert "total_sentences_evaluated" in summary
    assert "grounded_sentences_pct" in summary
    assert "regenerated_sentences_pct" in summary
    assert "unresolved_flagged_pct" in summary
    assert "mean_voice_distinctiveness_score" in summary
    assert "template_collision_rate_pct" in summary
    assert summary["template_collision_rate_pct"] == 0.0

@pytest.mark.asyncio
async def test_voice_distinctiveness_and_anti_templating_regression():
    payload = {
        "question": "What do these philosophers teach about facing death and mortality?",
        "thinkers": ["marcus_aurelius", "friedrich_nietzsche", "immanuel_kant", "lao_tzu"],
        "session_id": "test_voice_regression"
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["template_collision"] is False
    assert data["voice_distinctiveness_score"] >= 0.85
    
    breakdown_map = {b["thinker_id"]: b for b in data["per_thinker_breakdown"]}
    assert len(breakdown_map) == 4
    
    # 1. Laozi: Must contain Daoist concepts, MUST NOT contain Stoic boilerplate
    laozi_text = (breakdown_map["lao_tzu"]["core_stance"] + " " + breakdown_map["lao_tzu"]["detailed_argument"]).lower()
    assert any(term in laozi_text for term in ["dao", "wu wei", "yielding", "water", "harmony", "ziran"])
    assert "rational agency" not in laozi_text
    assert "disciplined judgment" not in laozi_text
    assert "unshakeable integrity" not in laozi_text
    
    # 2. Nietzsche: Must contain Existentialist/Will to Power concepts, MUST NOT contain Stoic boilerplate
    nietzsche_text = (breakdown_map["friedrich_nietzsche"]["core_stance"] + " " + breakdown_map["friedrich_nietzsche"]["detailed_argument"]).lower()
    assert any(term in nietzsche_text for term in ["will to power", "amor fati", "overcoming", "creative"])
    assert "rational agency" not in nietzsche_text
    assert "disciplined judgment" not in nietzsche_text
    assert "universal moral duty" not in nietzsche_text
    
    # 3. Kant: Must contain Deontological/Categorical Imperative concepts
    kant_text = (breakdown_map["immanuel_kant"]["core_stance"] + " " + breakdown_map["immanuel_kant"]["detailed_argument"]).lower()
    assert any(term in kant_text for term in ["categorical imperative", "practical reason", "moral law", "duty", "dignity"])
    assert "wu wei" not in kant_text
    
    # 4. Aurelius: Must contain Stoic/Cosmic Nature concepts
    aurelius_text = (breakdown_map["marcus_aurelius"]["core_stance"] + " " + breakdown_map["marcus_aurelius"]["detailed_argument"]).lower()
    assert any(term in aurelius_text for term in ["governing mind", "hegemonikon", "nature", "logos", "dissolution", "tranquility", "stoic"])
    assert "wu wei" not in aurelius_text

@pytest.mark.asyncio
async def test_dialectical_synthesis_section_diversity_and_no_repeated_corrupted_text():
    payload = {
        "question": "What do Marcus Aurelius, Aristotle, Kant, Nietzsche, and Laozi teach regarding the morality of taking human life and ethical duty?",
        "thinkers": ["marcus_aurelius", "aristotle", "immanuel_kant", "friedrich_nietzsche", "lao_tzu"],
        "session_id": "test_ethics_diversity"
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    answer = data["answer"]
    
    # 1. Verify all four sections are present
    assert "### 1. Dialectical Overview" in answer
    assert "### 2. Points of Convergence" in answer
    assert "### 3. Fundamental Clashes & Divergences" in answer
    assert "### 4. Philosophical Synthesis & Takeaway" in answer
    
    # 2. Verify no corrupted slicing fragments exist in answer
    corrupted_fragments = [
        "dawn when trouble getting",
        "when trouble getting guides",
        "getting guides human judgment",
        "as directly affirmed in as directly",
        "trouble getting guides"
    ]
    for frag in corrupted_fragments:
        assert frag not in answer.lower(), f"Corrupted fragment '{frag}' found in synthesis output!"
        
    # 3. Verify sections have distinct, non-duplicated text
    sections = [s.strip() for s in answer.split("###") if s.strip()]
    assert len(sections) == 4
    
    bodies = ["\n".join(s.split("\n")[1:]).strip() for s in sections]
    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            assert bodies[i] != bodies[j], f"Section {i} and Section {j} have duplicate body content!"
            assert len(bodies[i]) > 40, f"Section {i} is too short or empty!"

@pytest.mark.asyncio
async def test_claim_regeneration_coherence_and_well_formedness():
    from app.core.guardrails import is_sentence_coherent, guardrails_manager
    from app.core.llm import llm_service
    from app.rag.schema import Chunk

    context = (
        "[Meditations, Book V, Section 1]: At dawn, when you have trouble getting out of bed, "
        "tell yourself: 'I have to go to work—as a human being. What do I have to complain of, "
        "if I'm going to do what I was born for?'"
    )

    # 1. Verify corrupted fragments fail coherence check
    assert not is_sentence_coherent("Meditations establishes that dawn when trouble getting guides human judgment and ethical action.")
    assert not is_sentence_coherent("dawn when trouble getting out of bed.")
    assert not is_sentence_coherent("when trouble getting guides human.")

    # 2. Test regeneration of an ungrounded Marcus Aurelius claim
    flagged_claim = "Marcus Aurelius (Roman Stoicism) emphasizes Marcus Aurelius and asserts ungrounded claims."
    regenerated = llm_service.regenerate_sentence(flagged_claim, context)
    
    assert is_sentence_coherent(regenerated)
    assert "dawn when trouble getting" not in regenerated.lower()
    assert "marcus aurelius" in regenerated.lower()
    assert regenerated.endswith(".")

    # 3. Test check_and_resolve_sentences preserves clean text when ungrounded
    chunks_dict = {
        "marcus_aurelius": [
            Chunk(
                id="ma_01",
                thinker_id="marcus_aurelius",
                thinker_name="Marcus Aurelius",
                tradition="Roman Stoicism",
                work_title="Meditations",
                chapter="Book V, Section 1",
                text="At dawn, when you have trouble getting out of bed, tell yourself: I have to go to work as a human being.",
                score=0.95
            )
        ]
    }
    answer = "In Meditations, Book V, Section 1, Marcus Aurelius teaches that rising at dawn to perform purposeful work is the fundamental duty of a human being aligned with nature."
    res_ans, s_list, r_logs, faith, flags = guardrails_manager.check_and_resolve_sentences(answer, chunks_dict)
    assert len(s_list) >= 1
    assert s_list[0].grounded is True
    assert faith >= 0.70

@pytest.mark.asyncio
async def test_evaluation_benchmark_metrics():
    from app.core.evaluator import evaluator_service
    summary = await evaluator_service.run_evaluation()
    
    assert summary.total_evaluations == 8
    assert summary.mean_faithfulness >= 0.75, f"Expected faithfulness >= 0.75, got {summary.mean_faithfulness}"
    assert summary.mean_context_recall >= 0.65, f"Expected context recall >= 0.65, got {summary.mean_context_recall}"
    assert summary.retrieval_mismatch_rate_pct <= 15.0, f"Expected mismatch rate <= 15%, got {summary.retrieval_mismatch_rate_pct}%"
    assert summary.unresolved_flagged_pct <= 10.0, f"Expected unresolved rate <= 10%, got {summary.unresolved_flagged_pct}%"
    assert summary.grounded_sentences_pct >= 75.0, f"Expected grounded sentences >= 75%, got {summary.grounded_sentences_pct}%"
    assert summary.template_collision_rate_pct == 0.0

@pytest.mark.asyncio
async def test_abstract_query_expansion_and_retrieval_alignment():
    """
    Verifies that abstract philosophical queries (suffering, society/friendship, death/mortality)
    trigger thinker-specific conceptual expansion and achieve 'Aligned' retrieval status with high recall.
    """
    from app.graph.workflow import run_query_workflow

    # 1. Test Suffering Abstract Query
    q1 = "What is the meaning and purpose of suffering in human life?"
    res1 = await run_query_workflow(q1, requested_thinkers=["friedrich_nietzsche", "marcus_aurelius", "lao_tzu"], session_id="test_suf")
    assert res1.is_weak_match is False
    assert res1.topic_alignment_score >= 0.70
    citations_text1 = " ".join([c.quote.lower() for c in res1.citations])
    assert any(term in citations_text1 for term in ["suffering", "pain", "citadel", "yielding", "water"])

    # 2. Test Society & Friendship Abstract Query
    q2 = "What constitutes a virtuous life in relation to society and friendship?"
    res2 = await run_query_workflow(q2, requested_thinkers=["aristotle", "marcus_aurelius", "immanuel_kant"], session_id="test_soc")
    assert res2.is_weak_match is False
    assert res2.topic_alignment_score >= 0.70
    citations_text2 = " ".join([c.quote.lower() for c in res2.citations])
    assert any(term in citations_text2 for term in ["friendship", "philia", "political animal", "cooperation", "humanity as an end"])

    # 3. Test Multi-Thinker Death & Mortality Abstract Query
    q3 = "What do Marcus Aurelius, Nietzsche, Kant, and Laozi teach about facing death and mortality?"
    res3 = await run_query_workflow(q3, requested_thinkers=["marcus_aurelius", "friedrich_nietzsche", "immanuel_kant", "lao_tzu"], session_id="test_death")
    assert res3.is_weak_match is False
    assert res3.topic_alignment_score >= 0.70

@pytest.mark.asyncio
async def test_novel_out_of_sample_queries_generalization():
    """
    Validates that novel emotional, interpersonal, and psychological queries outside the golden benchmark
    (e.g., bullying, betrayal, jealousy, public humiliation, anxiety) retrieve authentic thematic passages
    and never revert to generic default chunks (like ma_med_04).
    """
    from app.graph.workflow import run_query_workflow

    novel_tests = [
        ("How would they react to being bullied?", ["marcus_aurelius", "friedrich_nietzsche", "lao_tzu"]),
        ("How would they handle betrayal by a close friend?", ["marcus_aurelius", "aristotle", "immanuel_kant"]),
        ("What would they say about overcoming jealousy and envy?", ["marcus_aurelius", "friedrich_nietzsche", "aristotle"]),
        ("How should one respond to public humiliation and insults?", ["marcus_aurelius", "lao_tzu", "immanuel_kant"]),
        ("What is the ethical response to unprovoked aggression and hostility?", ["marcus_aurelius", "aristotle", "lao_tzu"])
    ]

    for q, thinkers in novel_tests:
        res = await run_query_workflow(q, requested_thinkers=thinkers, session_id=f"test_novel_{hash(q)}")
        aurelius_cits = [c for c in res.citations if c.thinker_name == "Marcus Aurelius"]
        if aurelius_cits:
            top_ma = aurelius_cits[0]
            # Verify Aurelius NEVER returns ma_med_04 (the dawn/morning routine chunk) for interpersonal/emotional queries
            assert top_ma.chunk_id != "ma_med_04", f"Query '{q}' defaulted to generic ma_med_04 chunk!"
            # Verify top chunk is an authentic interpersonal/resilience passage (ma_med_01, ma_med_02, ma_med_03, or ma_med_05)
            assert top_ma.chunk_id in ["ma_med_01", "ma_med_02", "ma_med_03", "ma_med_05", "ma_med_08"]




