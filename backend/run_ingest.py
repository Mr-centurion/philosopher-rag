#!/usr/bin/env python3
"""
Standalone CLI script to pre-ingest the philosophical corpus into ChromaDB and build BM25 indices.
"""
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.rag.ingest import ingestion_pipeline

def main():
    print("=" * 60)
    print("🏛️  Comparative Philosophy RAG - Corpus Ingestion Pipeline")
    print("=" * 60)
    ingestion_pipeline.run()
    thinkers = ingestion_pipeline.get_thinkers_metadata()
    print("\n📊 Ingested Philosophers:")
    for t in thinkers:
        print(f"  • {t.name:<22} | Tradition: {t.tradition:<32} | Chunks: {t.chunk_count:<3} | Words: {t.word_count}")
    print("\n✅ Ingestion finished successfully.")

if __name__ == "__main__":
    main()
