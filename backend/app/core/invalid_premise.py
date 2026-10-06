import re
from typing import Optional, Tuple, List, Dict

# Known modern entities, figures, brands, and pop culture references with no classical philosophical grounding
INVALID_PREMISE_PATTERNS: List[Tuple[str, str, str, List[str]]] = [
    # 1. Modern content creators, influencers, internet personalities
    (
        r"\b(pewdiepie|mrbeast|joe\s+rogan|logan\s+paul|jake\s+paul|andrew\s+tate|kai\s+cenat|ishowspeed|pokimane|ninja|streamer|streamers|youtuber|youtubers|tiktoker|tiktokers|influencer|influencers)\b",
        "Modern Internet Personality / Content Creator",
        "modern internet content creators and online influencers",
        [
            "How do Marcus Aurelius, Seneca, and Epictetus view the pursuit of public admiration, fame, and transient social acclaim?",
            "What is the distinction between intrinsic moral character and superficial external reputation?",
            "How do classical thinkers advise dealing with public applause and the fickle judgment of the crowd?"
        ]
    ),
    # 2. Modern celebrities, pop culture figures, entertainment stars
    (
        r"\b(kardashian|kardashians|taylor\s+swift|kanye|drake|beyonce|bieber|hollywood\s+celebrity|pop\s+star|celebrity\s+gossip|reality\s+tv)\b",
        "Modern Celebrity / Pop Icon",
        "contemporary pop celebrities and commercial entertainment figures",
        [
            "What do Seneca and Aristotle teach regarding the illusion of worldly status and public flattery?",
            "What constitutes genuine human flourishing (Eudaimonia) versus transient celebrity and amusement?",
            "How does Stoic philosophy counsel guarding the mind against the seduction of public prestige?"
        ]
    ),
    # 3. Modern consumer finance, credit cards, banking instruments, cryptocurrency
    (
        r"\b(credit\s+cards?|debit\s+cards?|crypto|cryptocurrency|cryptocurrencies|bitcoin|ethereum|dogecoin|nfts?|blockchain|cashback|credit\s+score|fiat\s+currency|stock\s+market|wall\s+street|hedge\s+fund)\b",
        "Modern Financial / Commercial Instrument",
        "modern commercial banking instruments and speculative financial systems",
        [
            "What do Aristotle, Seneca, and Laozi teach regarding wealth, desire, debt, and the limits of material acquisition?",
            "How does the compulsive pursuit of material profit and borrowing compromise personal autonomy and tranquility?",
            "What constitutes the boundary between necessary economic provisions and unrestrained acquisitiveness (Chrematistike)?"
        ]
    ),
    # 4. Modern consumer gadgets, tech products, smartphones, consumer hardware
    (
        r"\b(iphones?|ipads?|smartphones?|cell\s+phones?|macbooks?|airpods?|playstations?|xbox|smart\s+watches?|laptops?|gadgets?)\b",
        "Modern Consumer Electronics / Gadget",
        "contemporary consumer electronics and mobile hardware",
        [
            "How does Seneca advise guarding one's attention and tranquility against external tools of constant distraction?",
            "What constitutes the mastery of personal desires versus dependence upon artificial contrivances?",
            "How does Stoicism distinguish between natural necessities and artificial, superfluous dependencies?"
        ]
    ),
    # 5. Social media platforms and modern digital engagement apps
    (
        r"\b(tiktoks?|instagram|twitter|x\s+app|snapchat|facebook|reddits?|tinder|bumble|social\s+media\s+apps?|dating\s+apps?)\b",
        "Social Media Platform / Digital Entertainment",
        "modern algorithmic social networks and digital engagement platforms",
        [
            "What is the Stoic and Daoist counsel regarding solitude, inward reflection, and immunity to public spectacle?",
            "How does continuous social comparison and seeking peer validation erode peace of mind (Ataraxia)?",
            "What are the philosophical dangers of substituting virtual appearances for genuine virtue and friendship (Philia)?"
        ]
    ),
    # 6. Video games, pop culture franchises, anime
    (
        r"\b(video\s+games?|gaming|fortnite|minecraft|call\s+of\s+duty|league\s+of\s+legends|anime|manga|superheroes?|marvel|avengers?|star\s+wars|batman|superman)\b",
        "Modern Video Game / Pop Culture Franchise",
        "contemporary commercial video games and cinematic entertainment franchises",
        [
            "What is the philosophical role of leisure, play, and entertainment versus the cultivation of wisdom and virtue?",
            "How did ancient thinkers distinguish between illusory spectacles and genuine contemplation of truth?",
            "What constitutes true heroism and courage according to Classical Greek and Stoic traditions?"
        ]
    ),
    # 7. Modern corporate brands and fast-food chains
    (
        r"\b(nike|adidas|mcdonalds?|starbucks|coca[- ]cola|pepsi|walmart|amazon\s+prime|tesla|uber|lyft)\b",
        "Commercial Brand / Corporation",
        "contemporary corporate commercial brands and consumer franchises",
        [
            "What is the ethical distinction between natural human needs and manufactured commercial appetites?",
            "How do classical sages view moderation (Sophrosyne) and simplicity in contrast to commercial excess?",
            "What does ancient political philosophy teach regarding commerce, civic virtue, and the common good?"
        ]
    )
]

def detect_invalid_premise(question: str) -> Optional[Tuple[str, str, str, List[str]]]:
    """
    Examines whether the query references a modern entity, commercial product, pop culture figure,
    or anachronism that has no genuine grounding in classical philosophical texts.
    Returns: (matched_entity, category_name, category_description, suggested_philosophical_questions)
    """
    q_lower = question.lower()
    for pattern, cat_name, cat_desc, suggestions in INVALID_PREMISE_PATTERNS:
        match = re.search(pattern, q_lower)
        if match:
            entity = match.group(0)
            return (entity, cat_name, cat_desc, suggestions)
    return None

def build_invalid_premise_response(question: str, entity: str, category_desc: str, suggestions: List[str]) -> str:
    """
    Constructs a clear, honest, and scholarly response explaining the historical boundary
    and providing relevant foundational inquiries the user can explore instead.
    """
    sugg_bullets = "\n".join([f"- \"{s}\"" for s in suggestions])
    
    return (
        f"### Historical & Conceptual Boundary: Inquiry Without Primary Text Grounding\n\n"
        f"The inquiry into \"{question}\" centers on \"{entity}\"—a concept belonging to {category_desc}. "
        f"This subject does not correspond to a genuine philosophical inquiry or doctrine addressed within the primary texts of our indexed thinkers.\n\n"
        f"Ancient Stoics (Marcus Aurelius, Seneca, Epictetus), Classical Greek philosophers (Plato, Aristotle), "
        f"Enlightenment thinkers (Voltaire), and Eastern traditions (Laozi, Bhagavad Gita, Chanakya) formulated doctrines "
        f"concerning timeless ethics, human suffering, virtue, duty, and cosmic order—not contemporary commercial entities, "
        f"digital influencers, or modern cultural phenomena.\n\n"
        f"Because our primary source retrieval returned no direct textual treatises on this subject, generating a multi-thinker dialectical "
        f"synthesis would fabricate speculative positions rather than providing rigorous, source-grounded scholarship.\n\n"
        f"#### Closer Foundational Questions You Might Meaningfully Explore:\n"
        f"{sugg_bullets}"
    )
