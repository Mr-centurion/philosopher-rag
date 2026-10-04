import re
import logging
from typing import List, Dict, Tuple, Optional
from app.rag.schema import Chunk

logger = logging.getLogger("philosophy_rag.topic_matcher")

TOPIC_SYNONYMS: Dict[str, List[str]] = {
    "death": [
        "death", "dying", "mortality", "mortal", "memento mori", "depart", "departing",
        "perish", "end of life", "grave", "funeral", "corpse", "dissolution", "mortal cycle",
        "mystery of nature", "elements", "eternal", "returns to its root", "root", "stillness"
    ],
    "suffering": [
        "suffering", "pain", "hardship", "adversity", "grief", "agony", "torment", "endure",
        "endurance", "wound", "unbearable", "bearable", "bear", "curse", "guilt", "penance",
        "misfortune", "ascetic ideals", "meaning of suffering", "citadel", "yielding",
        "softness", "water", "trouble"
    ],
    "duty": [
        "duty", "imperative", "obligation", "moral law", "ought", "maxims", "command",
        "universal law", "categorical imperative", "good will", "kingdom of ends",
        "unselfish action", "work as a human being"
    ],
    "virtue": [
        "virtue", "arete", "excellence", "character", "habit", "moral virtue", "courage",
        "temperance", "justice", "phronesis", "practical wisdom", "doctrine of the mean",
        "mesotes", "liberality"
    ],
    "happiness": [
        "happiness", "eudaimonia", "flourishing", "well-being", "fulfillment", "joy",
        "peace", "chief good", "function of man", "tranquility", "activity of soul"
    ],
    "desire": [
        "desire", "passion", "appetite", "inclination", "attachment", "craving", "lust",
        "volition", "objects of volition"
    ],
    "action": [
        "action", "wu wei", "non-action", "activity", "practice", "deeds", "striving",
        "activity of soul", "impediment to action advances action", "effortless", "yielding"
    ],
    "power": [
        "power", "will to power", "strength", "overcoming", "force", "mastery", "domination",
        "discharge its strength", "noble", "overman", "ubermensch"
    ],
    "society": [
        "society", "friendship", "philia", "friend", "companion", "political animal",
        "zoon politikon", "cooperation", "fellow man", "made for each other", "community",
        "humanity as an end", "kingdom of ends", "persons"
    ],
    "friendship": [
        "friendship", "philia", "friend", "companion", "society", "political animal",
        "cooperation", "fellow man", "made for each other", "community", "humanity as an end"
    ],
    "insult": [
        "bullied", "bullying", "bully", "insult", "insults", "insulted", "mockery", "ridicule",
        "taunt", "taunting", "harassment", "abuse", "contempt", "scorn", "disrespect", "slight",
        "humiliation", "humiliated", "shame", "disgrace", "provocation", "provoked", "meddling",
        "arrogant", "dishonest", "wrongdoer", "blame", "hate", "criticism", "criticisms",
        "injure", "injury", "harm", "assents to being wounded", "citadel", "offense"
    ],
    "harm": [
        "harm", "hurt", "injury", "insult", "citadel", "governing mind", "wound",
        "judgment", "assents to being wounded", "autonomy", "choose not to be harmed"
    ],
    "betrayal": [
        "betrayal", "betrayed", "betray", "treachery", "deceit", "deceived", "disloyalty",
        "backstabbing", "unfaithful", "dishonest", "false friend", "friend", "philia",
        "companion", "society"
    ],
    "jealousy": [
        "jealousy", "jealous", "envy", "envious", "covet", "covetousness", "resentment",
        "ressentiment", "bitterness", "grudge", "spite", "malice", "ugliness", "surly"
    ],
    "loneliness": [
        "loneliness", "lonely", "isolation", "isolated", "solitude", "alone", "alienation",
        "retreat into yourself", "soul", "citadel", "fellow man", "cooperation", "friendship",
        "loneliest loneliness"
    ],
    "anxiety": [
        "anxiety", "anxious", "fear", "afraid", "panic", "dread", "worry", "worried",
        "troubled", "unbearable", "future", "present moment", "serenity", "stillness", "tranquility"
    ],
    "aggression": [
        "aggression", "aggressive", "hostility", "hostile", "attack", "attacking", "violence",
        "violent", "conflict", "quarrel", "enemy", "war", "school of war", "will to power",
        "water", "yielding", "does not contend"
    ],
    "leadership": [
        "leader", "leadership", "lead", "governing", "ruler", "king", "maintain order",
        "sage", "subordinates", "model for the world", "kingdom of ends", "state",
        "arrogant subordinates", "corrupt"
    ],
    "nature": [
        "nature", "natural", "cosmos", "providence", "dao", "tao", "logos", "water", "way"
    ],
    "morality": [
        "morality", "moral", "ethics", "ethical", "good and evil", "good will",
        "imperative", "master morality", "slave morality", "virtue", "ought", "values",
        "human life"
    ],
    "anger": [
        "anger", "wrath", "rage", "resentment", "ressentiment", "hatred", "bitterness"
    ],
    "god": [
        "god", "divine", "logos", "heavens", "cosmos", "providence", "nature", "dao", "tao"
    ]
}

# Thinker/Tradition-specific conceptual vocabulary for nuanced philosophical mapping
THINKER_TRADITION_VOCABULARY: Dict[str, Dict[str, List[str]]] = {
    "marcus_aurelius": {
        "insult": ["meddling", "ungrateful", "arrogant", "dishonest", "surly", "cannot hurt me", "no one can implicate me in ugliness", "nor can i feel angry", "we were made for cooperation", "choose not to be harmed", "governing mind", "soul is its own citadel", "assent to being wounded", "insults of others", "learn to bear them", "blames or hates you", "no reason to torment yourself", "wrongdoer"],
        "betrayal": ["wrongdoer has a nature related to my own", "same mind", "cannot hurt me", "made for cooperation", "learn to bear them", "governing mind", "fellow man"],
        "jealousy": ["retreat into yourself", "good order", "fundamental principles", "cleanse your spirit", "without resentment", "soul is its own citadel", "jealous"],
        "loneliness": ["retreat into yourself", "quieter or more untroubled retreat", "own soul", "good order", "we were made for cooperation", "like feet like hands"],
        "anxiety": ["present moment", "cannot lose either past or future", "regulate every act and thought", "serene mind", "objective judgment", "willing acceptance", "trouble"],
        "leadership": ["meddling ungrateful arrogant", "wrongdoer related to my own", "made for cooperation", "teach them or learn to bear them", "no reason to torment yourself", "governing mind"],
        "aggression": ["cannot hurt me", "no one can implicate me in ugliness", "nor can i feel angry", "choose not to be harmed", "impediment advances action"],
        "suffering": ["pain", "unbearable", "bearable", "ruling center", "citadel", "governing mind", "assents to being wounded", "soul", "complaint", "lamentation", "suffering"],
        "society": ["cooperation", "fellow man", "made for each other", "wrongdoer", "same mind", "divine", "upper and lower teeth", "act against each other", "bear them"],
        "friendship": ["cooperation", "fellow man", "made for each other", "wrongdoer", "same mind", "divine", "bear them"],
        "death": ["depart from life", "death", "mortal cycle", "natural completion", "actor dismissed from the stage", "elements", "resolving into the same elements", "mystery of nature", "present moment", "facing death", "depart", "dissolution", "mortal"],
        "harm": ["choose not to be harmed", "governing mind", "citadel", "assent to being wounded", "loss of wealth", "insults of others"],
        "duty": ["job as a human being", "what nature demands", "objective judgment", "unselfish action", "willing acceptance", "impediment advances action"],
        "morality": ["good and evil", "wrongdoer", "share of the divine", "nature demands", "objective judgment", "unselfish action", "human life"]
    },
    "friedrich_nietzsche": {
        "insult": ["ressentiment", "slave morality", "master morality", "noble type of man", "what is harmful to me is harmful in itself", "value-creating", "contempt", "school of war", "what does not kill me makes me stronger", "overcoming"],
        "betrayal": ["ressentiment", "slave morality", "noble type of man", "determining values", "value-creating", "lion"],
        "jealousy": ["ressentiment", "slave morality", "noble type of man", "will to power", "determining values", "looking away shall be my only negation", "yes-sayer"],
        "loneliness": ["loneliest loneliness", "demon", "greatest weight", "eternal recurrence", "overman", "lightning out of dark cloud"],
        "aggression": ["school of war", "what does not kill me makes me stronger", "will to power", "discharge its strength", "lion", "sacred yes"],
        "suffering": ["ascetic ideals", "meaning of suffering", "curse", "guilt and penance", "what does not kill me makes me stronger", "school of war", "why in life", "overcoming", "amor fati", "every pain and every joy", "meaninglessness of suffering"],
        "death": ["amor fati", "eternal recurrence", "yes-sayer", "demon", "greatest weight", "innumerable times more", "overman", "lightning out of dark cloud", "free death", "overcome man"],
        "society": ["master morality", "slave morality", "ressentiment", "utility", "sympathy", "kindness", "humility", "noble type of man", "burdens of tradition"],
        "friendship": ["noble type of man", "determining values", "value-creating", "lion", "sacred yes"],
        "morality": ["master morality", "slave morality", "ressentiment", "value-creating", "will to power", "noble", "good and evil"],
        "action": ["discharge its strength", "will to power", "lion", "child", "sacred yes", "conquers his own world", "striving"],
        "happiness": ["school of war", "why in life", "man does not strive after happiness", "will to power", "discharge strength"]
    },
    "immanuel_kant": {
        "insult": ["humanity as an end", "never merely as a means", "rational beings are called persons", "ends in themselves", "ought not to be used merely as a means", "good will", "courage and resolution", "sapere aude"],
        "leadership": ["kingdom of ends", "gives universal laws", "autonomy of the will", "categorical imperative", "moral law", "rational beings"],
        "betrayal": ["act only according to that maxim", "universal law", "humanity as an end", "rational beings are called persons"],
        "society": ["humanity as an end", "kingdom of ends", "rational beings", "persons", "never merely as a means", "ends in themselves", "member to the kingdom of ends"],
        "friendship": ["humanity as an end", "kingdom of ends", "rational beings", "persons", "never merely as a means"],
        "duty": ["categorical imperative", "good will", "universal law", "maxim", "moral law", "ought", "autonomy of the will", "heteronomy"],
        "morality": ["good will", "categorical imperative", "universal law", "moral law within", "humanity as an end", "autonomy", "kingdom of ends"],
        "suffering": ["autonomy", "good will", "moral law within", "courage", "perseverance", "heteronomy"],
        "death": ["duty", "imperative", "categorical imperative", "moral law", "good will", "kingdom of ends", "highest good", "rational beings", "starry heavens"],
        "harm": ["good will", "autonomy", "heteronomy", "moral law", "courage", "resolution"]
    },
    "aristotle": {
        "insult": ["doctrine of the mean", "courage is the mean between fear and confidence", "just acts", "political animal", "phronesis", "practical wisdom"],
        "betrayal": ["friendship", "philia", "without friends no one would choose to live", "in misfortunes friends are the only refuge", "perfect friendship", "wish well alike"],
        "leadership": ["political animal", "deliberate well", "good life in general", "practical wisdom", "just and unjust"],
        "society": ["political animal", "zoon politikon", "without a state", "gift of speech", "logos", "just and unjust", "friendship", "philia", "community"],
        "friendship": ["friendship", "philia", "without friends no one would choose to live", "in misfortunes friends are the only refuge", "perfect friendship", "wish well alike", "political animal"],
        "virtue": ["moral virtue", "habit", "ethos", "doctrine of the mean", "mesotes", "phronesis", "practical wisdom", "courage", "temperance", "liberality", "just acts"],
        "happiness": ["eudaimonia", "chief good", "function of man", "activity of soul", "excellence", "arete", "flourishing", "habit"],
        "action": ["activity of soul", "function of man", "habit", "exercise the activity", "doing just acts", "eudaimonia"],
        "suffering": ["misfortunes", "friends are the only refuge", "courage", "mean between fear and confidence", "endure"],
        "morality": ["virtue", "arete", "doctrine of the mean", "phronesis", "aim at some good", "chief good", "just acts", "political animal"]
    },
    "lao_tzu": {
        "insult": ["softness overcomes hardness", "water", "yielding", "does not contend", "no one in the world can contend with him", "bend and remain straight", "worn out and remain renewed", "supreme good like water", "stays in places others despise"],
        "betrayal": ["in relations be benevolent", "in speaking be trustworthy", "does not contend", "without fault", "yield and remain whole"],
        "loneliness": ["attain utmost emptiness", "maintain steadfast tranquility", "returns to its root", "stillness", "returning to destiny", "eternal", "enlightenment"],
        "leadership": ["in governing maintain order", "sage embraces the one", "model for the world", "not showing off therefore enlightened", "not self-righteous", "not arrogant therefore enduring", "world is won by letting things take natural course"],
        "aggression": ["softness overcomes hardness", "water benefits all things and does not compete", "does not contend therefore without fault", "gentle overcomes rigid"],
        "suffering": ["yielding", "softness overcomes hardness", "water", "bend and remain straight", "worn out and remain renewed", "hollow and remain full", "does not contend"],
        "death": ["returns to its root", "stillness", "destiny", "eternal", "enlightenment", "all things arise together", "watch their return", "natural course", "yielding", "bend and remain straight", "softness"],
        "society": ["benevolent", "trustworthy", "maintain order", "does not compete", "without fault", "model for the world", "sage embraces the one"],
        "friendship": ["benevolent", "trustworthy", "does not compete", "without fault", "yielding", "softness"],
        "action": ["wu wei", "non-action", "action of non-action", "less and less is done", "natural course", "without interference", "water"],
        "happiness": ["wu wei", "supreme good like water", "stillness", "without desire", "simplicity", "tranquility", "water"],
        "harm": ["softness overcomes hardness", "water", "cannot contend", "yield and remain whole", "emptiness"],
        "morality": ["supreme good like water", "benevolent", "trustworthy", "dao", "wu wei", "goodness as good", "not self-righteous"]
    }
}

STOPWORDS = {
    "what", "does", "say", "about", "how", "why", "who", "when", "where", "is", "are",
    "the", "a", "an", "and", "or", "in", "on", "to", "for", "with", "by", "from",
    "aurelius", "nietzsche", "kant", "aristotle", "laozi", "lao", "tzu", "marcus",
    "friedrich", "immanuel", "think", "explain", "view", "teach", "tell", "me",
    "taking", "regarding", "between", "human", "life", "relation", "constitutes",
    "conflict", "personal", "universal", "achieved", "through", "active", "effortless",
    "facing", "would", "they", "being", "should", "one", "their", "respond", "react",
    "advice", "coping", "deal"
}

class TopicMatcher:
    def __init__(self):
        self.topic_synonyms = TOPIC_SYNONYMS
        self.tradition_vocabulary = THINKER_TRADITION_VOCABULARY

    def extract_core_topics(self, question: str) -> List[str]:
        """
        Extracts key noun/topic phrases from the user's question, ignoring philosopher names and filler words.
        """
        clean_q = question.lower().replace("?", "").replace(".", "").replace('"', '').replace("'", "")
        words = re.findall(r"\b[a-zA-Z]{3,}\b", clean_q)
        content_words = [w for w in words if w not in STOPWORDS]
        
        matched_topics = []
        for word in content_words:
            matched = False
            for root_topic, synonyms in TOPIC_SYNONYMS.items():
                if word in synonyms or word == root_topic:
                    matched_topics.append(root_topic)
                    matched = True
                    break
            if not matched:
                matched_topics.append(word)

        return list(dict.fromkeys(matched_topics)) if matched_topics else ["general_ethics"]

    def compute_topic_alignment(self, question: str, chunk: Chunk, thinker_id: Optional[str] = None) -> Tuple[float, bool]:
        """
        Computes the semantic and conceptual alignment score of a retrieved chunk against the query's core topics.
        Incorporates both universal topic synonyms and tradition-specific philosophical lexicons.
        Returns (alignment_score: float 0-1, is_topic_aligned: bool).
        """
        topics = self.extract_core_topics(question)
        chunk_text_lower = (chunk.text + " " + chunk.work_title + " " + chunk.chapter).lower()
        t_id = thinker_id or chunk.thinker_id
        t_vocab = THINKER_TRADITION_VOCABULARY.get(t_id, {})

        matched_synonyms_count = 0
        total_topics = len(topics)

        for topic in topics:
            synonyms = list(dict.fromkeys(TOPIC_SYNONYMS.get(topic, [topic]) + t_vocab.get(topic, [])))
            if any(syn.lower() in chunk_text_lower for syn in synonyms):
                matched_synonyms_count += 1

        topic_score = matched_synonyms_count / max(total_topics, 1)

        # Baseline alignment is true if topic_score >= 0.33 or any primary topic keyword is present
        is_aligned = topic_score >= 0.33 or any(
            any(syn.lower() in chunk_text_lower for syn in list(dict.fromkeys(TOPIC_SYNONYMS.get(t, [t]) + t_vocab.get(t, []))))
            for t in topics
        )

        return round(topic_score, 3), is_aligned

    def get_reformulated_query(self, question: str, thinker_id: str) -> str:
        """
        Generates a focused query explicitly boosting the specific topic and tradition-specific
        philosophical vocabulary for targeted re-retrieval.
        """
        topics = self.extract_core_topics(question)
        boost_terms = []
        t_vocab = THINKER_TRADITION_VOCABULARY.get(thinker_id, {})
        
        for t in topics:
            if t in t_vocab:
                boost_terms.extend(t_vocab[t][:6])
            else:
                boost_terms.extend(TOPIC_SYNONYMS.get(t, [t])[:4])

        thinker_name = thinker_id.replace("_", " ").title()
        boost_str = " ".join(list(dict.fromkeys(boost_terms)))
        
        return f"{thinker_name} {question} {boost_str}"

topic_matcher = TopicMatcher()
