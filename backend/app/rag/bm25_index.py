import re
from typing import List, Dict, Optional, Tuple
from rank_bm25 import BM25Okapi
from app.rag.schema import Chunk

STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have",
    "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers",
    "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm",
    "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's",
    "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off",
    "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out",
    "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should",
    "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their",
    "theirs", "them", "themselves", "then", "there", "there's", "these", "they",
    "they'd", "they'll", "they're", "they've", "this", "those", "through", "to",
    "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll",
    "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where",
    "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with",
    "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've",
    "your", "yours", "yourself", "yourselves"
}

def tokenize(text: str) -> List[str]:
    # Clean text, extract alphanumeric words, remove single letters and stopwords
    tokens = re.findall(r"\b[a-zA-Z]{2,}\b", text.lower())
    return [t for t in tokens if t not in STOPWORDS]

class BM25IndexManager:
    def __init__(self):
        self.indices: Dict[str, BM25Okapi] = {}
        self.corpus_chunks: Dict[str, List[Chunk]] = {}
        self.global_index: Optional[BM25Okapi] = None
        self.global_chunks: List[Chunk] = []

    def build_index(self, chunks: List[Chunk]):
        self.global_chunks = chunks
        tokenized_global = [tokenize(c.text + " " + c.work_title + " " + c.chapter) for c in chunks]
        self.global_index = BM25Okapi(tokenized_global)

        # Build per-thinker isolated indices
        by_thinker: Dict[str, List[Chunk]] = {}
        for c in chunks:
            by_thinker.setdefault(c.thinker_id, []).append(c)

        for thinker_id, t_chunks in by_thinker.items():
            self.corpus_chunks[thinker_id] = t_chunks
            tokenized = [tokenize(c.text + " " + c.work_title + " " + c.chapter) for c in t_chunks]
            self.indices[thinker_id] = BM25Okapi(tokenized)

    def search(self, query: str, thinker_id: Optional[str] = None, top_k: int = 5) -> List[Tuple[Chunk, float]]:
        tokenized_query = tokenize(query)
        if not tokenized_query:
            return []

        if thinker_id and thinker_id in self.indices:
            index = self.indices[thinker_id]
            chunks = self.corpus_chunks[thinker_id]
        else:
            if not self.global_index:
                return []
            index = self.global_index
            chunks = self.global_chunks

        raw_scores = index.get_scores(tokenized_query)
        max_score = max(raw_scores) if len(raw_scores) > 0 and max(raw_scores) > 0 else 1.0

        # Pair chunks with normalized BM25 score
        scored_pairs = []
        for chunk, score in zip(chunks, raw_scores):
            if score > 0:
                norm_score = float(score / max_score)
                scored_pairs.append((chunk, norm_score))

        scored_pairs.sort(key=lambda x: x[1], reverse=True)
        return scored_pairs[:top_k]

bm25_manager = BM25IndexManager()
