import json
import os
from pathlib import Path
from typing import List, Dict, Any
from app.config import settings
from app.rag.schema import Chunk, ThinkerMetadata
from app.rag.vector_store import vector_store
from app.rag.bm25_index import bm25_manager

THINKER_PROFILES = {
    "marcus_aurelius": {
        "name": "Marcus Aurelius",
        "tradition": "Roman Stoicism",
        "period": "121 – 180 CE",
        "color": "#eab308",  # Amber/Gold
        "avatar_url": "https://images.unsplash.com/photo-1544717305-2782549b5136?w=150&auto=format&fit=crop&q=80",
        "key_themes": ["Inner Citadel", "Dichotomy of Control", "Amor Fati", "Cosmopolitan Duty", "Transience (Memento Mori)"],
        "sample_quote": "You have power over your mind - not outside events. Realize this, and you will find strength."
    },
    "friedrich_nietzsche": {
        "name": "Friedrich Nietzsche",
        "tradition": "Continental Existentialism & Vitalism",
        "period": "1844 – 1900",
        "color": "#ef4444",  # Crimson Red
        "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80",
        "key_themes": ["Will to Power", "Master vs Slave Morality", "Amor Fati", "The Übermensch", "Eternal Recurrence"],
        "sample_quote": "He who has a why to live can bear almost any how."
    },
    "immanuel_kant": {
        "name": "Immanuel Kant",
        "tradition": "German Idealism & Deontology",
        "period": "1724 – 1804",
        "color": "#3b82f6",  # Sapphire Blue
        "avatar_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80",
        "key_themes": ["Categorical Imperative", "Duty & Good Will", "Humanity as an End", "Moral Autonomy", "Synthetic A Priori"],
        "sample_quote": "Two things awe me most: the starry heavens above me and the moral law within me."
    },
    "aristotle": {
        "name": "Aristotle",
        "tradition": "Classical Greek Virtue Ethics",
        "period": "384 – 322 BCE",
        "color": "#10b981",  # Emerald Green
        "avatar_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&auto=format&fit=crop&q=80",
        "key_themes": ["Eudaimonia (Flourishing)", "Doctrine of the Mean", "Habituation of Virtue", "Phronesis (Practical Wisdom)", "Teleology"],
        "sample_quote": "We are what we repeatedly do. Excellence, then, is not an act, but a habit."
    },
    "lao_tzu": {
        "name": "Laozi (Lao Tzu)",
        "tradition": "Ancient Eastern Daoism",
        "period": "6th – 4th Century BCE",
        "color": "#8b5cf6",  # Violet Purple
        "avatar_url": "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=150&auto=format&fit=crop&q=80",
        "key_themes": ["Wu Wei (Effortless Action)", "The Dao (The Way)", "Softness Overcoming Hardness", "Emptiness & Simplicity", "Harmony with Nature"],
        "sample_quote": "The journey of a thousand miles begins with a single step."
    }
}

class IngestionPipeline:
    def __init__(self):
        self.corpus_dir = Path(settings.CORPUS_DIR)
        self.loaded_chunks: List[Chunk] = []
        self.stats: Dict[str, Dict[str, int]] = {}

    def load_corpus(self) -> List[Chunk]:
        all_chunks = []
        stats = {}
        
        if not self.corpus_dir.exists():
            print(f"[Ingest] Corpus dir not found: {self.corpus_dir}")
            return []

        for json_file in sorted(self.corpus_dir.glob("*.json")):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                thinker_id = json_file.stem
                word_count = 0
                chunk_count = 0
                
                for item in data:
                    chunk = Chunk(
                        id=item["id"],
                        thinker_id=item["thinker_id"],
                        thinker_name=item["thinker_name"],
                        tradition=item["tradition"],
                        work_title=item["work_title"],
                        chapter=item["chapter"],
                        text=item["text"]
                    )
                    all_chunks.append(chunk)
                    word_count += len(item["text"].split())
                    chunk_count += 1
                    
                stats[thinker_id] = {
                    "word_count": word_count,
                    "chunk_count": chunk_count
                }
            except Exception as e:
                print(f"[Ingest] Error loading {json_file}: {e}")

        self.loaded_chunks = all_chunks
        self.stats = stats
        return all_chunks

    def run(self):
        print(f"[Ingest] Loading corpus from {self.corpus_dir}...")
        chunks = self.load_corpus()
        print(f"[Ingest] Loaded {len(chunks)} total chunks across {len(self.stats)} thinkers.")
        
        # 1. Populate Vector Store
        print("[Ingest] Indexing into ChromaDB vector store...")
        vector_store.add_chunks(chunks)

        # 2. Populate BM25 index
        print("[Ingest] Building BM25 index...")
        bm25_manager.build_index(chunks)
        print("[Ingest] Pipeline ingestion complete!")

    def get_thinkers_metadata(self) -> List[ThinkerMetadata]:
        if not self.loaded_chunks:
            self.load_corpus()
            
        thinkers = []
        for t_id, profile in THINKER_PROFILES.items():
            t_stats = self.stats.get(t_id, {"word_count": 0, "chunk_count": 0})
            thinkers.append(
                ThinkerMetadata(
                    id=t_id,
                    name=profile["name"],
                    tradition=profile["tradition"],
                    period=profile["period"],
                    avatar_url=profile["avatar_url"],
                    color=profile["color"],
                    key_themes=profile["key_themes"],
                    sample_quote=profile["sample_quote"],
                    word_count=t_stats["word_count"],
                    chunk_count=t_stats["chunk_count"]
                )
            )
        return thinkers

ingestion_pipeline = IngestionPipeline()
