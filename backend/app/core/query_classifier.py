import re
import logging
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel

logger = logging.getLogger("philosophy_rag.guardrails")

class QueryCategory(str, Enum):
    IN_SCOPE = "in_scope_philosophical"
    OFF_TOPIC = "off_topic"
    JAILBREAK = "jailbreak"
    HARMFUL_CONTENT_REQUEST = "harmful_content_request"

class ClassificationResult(BaseModel):
    category: QueryCategory
    is_safe: bool
    rejection_message: Optional[str] = None
    sub_category: Optional[str] = None
    matched_pattern: Optional[str] = None
    reason: Optional[str] = None

# Known philosophers (both indexed and broader tradition)
PHILOSOPHER_NAMES = {
    "marcus aurelius", "aurelius", "nietzsche", "friedrich nietzsche", "kant", "immanuel kant",
    "aristotle", "laozi", "lao tzu", "lao-tzu", "sun tzu", "plato", "socrates", "spinoza",
    "hume", "descartes", "schopenhauer", "epictetus", "seneca", "confucius", "kierkegaard",
    "hegel", "camus", "sartre", "wittgenstein", "locke", "hobbes", "rousseau", "aquinas"
}

# Core philosophical concepts and ethical themes (including personal moral/emotional dilemmas)
PHILOSOPHY_CONCEPTS = {
    "meaning", "purpose", "suffering", "death", "mortality", "virtue", "duty", "ethics",
    "ethical", "moral", "morality", "justice", "good", "evil", "free will", "destiny",
    "fate", "truth", "knowledge", "epistemology", "metaphysics", "eudaimonia", "dao",
    "tao", "wu wei", "amor fati", "categorical imperative", "inner citadel", "ruling center",
    "happiness", "soul", "mind", "reason", "rational", "rationality", "logic", "consciousness",
    "existential", "existentialism", "nihilism", "wisdom", "human nature", "nature",
    "conflict", "strategy", "philosophically", "philosophy", "philosophical", "society",
    "friendship", "philia", "lying", "lie", "bullied", "bullying", "betrayed", "betrayal",
    "jealousy", "envy", "insult", "humiliation", "aggression", "loneliness", "anxiety",
    "values", "god", "faith", "right and wrong", "virtuous", "character", "stoic", "stoicism",
    "harm", "inner", "self", "external", "events", "control", "tranquility", "serenity",
    "resilience", "endure", "endurance", "adversity", "autonomy", "integrity", "flourishing",
    "cooperation", "temperance", "moderation", "action", "choice", "desire", "imperative"
}

# Prompt Injection / Jailbreak patterns
JAILBREAK_PATTERNS = [
    (r"ignore\s+(all\s+|your\s+|the\s+)*(previous\s+|prior\s+|system\s+)?(instructions|prompts|rules|guidelines|directions)", "ignore_instructions"),
    (r"disregard\s+(all\s+|your\s+|the\s+)*(previous\s+|prior\s+|system\s+)?(instructions|prompts|rules|guidelines)", "disregard_instructions"),
    (r"pretend\s+(you\s+have|there\s+are)\s+no\s+(content\s+)?(restrictions|rules|filters|limits|guidelines)", "pretend_no_restrictions"),
    (r"pretend\s+you\s+are\s+(unfiltered|unrestricted|in\s+dan\s+mode|jailbroken|godmode|free\s+of\s+rules)", "pretend_unrestricted"),
    (r"you\s+are\s+now\s+in\s+dan\s+mode", "dan_mode"),
    (r"override\s+(all\s+|your\s+|the\s+)*(safety|system)\s+(guidelines|protocols|filters|rules)", "override_safety"),
    (r"reveal\s+(the\s+)?(system\s+prompt|initial\s+prompt|hidden\s+prompt|secret\s+key|instructions)", "reveal_system_prompt"),
    (r"forget\s+(all\s+|your\s+|the\s+)*(previous\s+|prior\s+|system\s+)?(instructions|restrictions|rules)", "forget_instructions"),
    (r"bypass\s+(all\s+|your\s+|the\s+)*(filters|safety|guardrails|restrictions)", "bypass_safety"),
    (r"act\s+as\s+an\s+unrestricted", "unrestricted_ai"),
]

# Dedicated Harmful Content Patterns (High Sensitivity)
HARMFUL_PATTERNS = [
    # 1. Misogyny & Gender-based discrimination/inferiority
    (r"(explain|argue|justify|prove|demonstrate|show)\s+(why|that)\s+women\s+are\s+(intellectually\s+|morally\s+|naturally\s+|inherently\s+)?inferior", "misogyny"),
    (r"justify\s+(why\s+)?men\s+should\s+dominate\s+women", "misogyny"),
    (r"(justify|argue\s+for|defend)\s+(the\s+)?(subjugation|inferiority|oppression|enslavement)\s+of\s+women", "misogyny"),
    (r"why\s+women\s+(should\s+be\s+subservient|belong\s+in\s+the\s+kitchen|should\s+have\s+no\s+rights|are\s+inferior)", "misogyny"),
    (r"women\s+are\s+(intellectually|morally|naturally)\s+inferior\s+to\s+men", "misogyny"),
    (r"justify\s+(violence|harm|abuse)\s+against\s+women", "misogyny"),

    # 2. Religious extremism & violence
    (r"(using\s+[\w\s]+,\s+)?explain\s+why\s+.*(religious\s+group|muslims?|jews?|christians?|hindus?).*deserves?\s+violence", "religious_extremism"),
    (r"(justify|call\s+for|advocate\s+for|incite)\s+holy\s+war(\s+against\s+non-believers)?", "religious_extremism"),
    (r"(justify|advocate|endorse)\s+(violence|harm|killing|slaughter|extermination)\s+against\s+(non-believers|infidels|religious\s+groups?|heretics)", "religious_extremism"),
    (r"why\s+(a\s+religious\s+group|any\s+religion)\s+(deserves\s+violence|is\s+evil|should\s+be\s+eradicated)", "religious_extremism"),
    (r"as\s+a\s+philosopher\s+would\s+argue,\s+justify\s+holy\s+war", "religious_extremism"),

    # 3. Weapons, explosives, and CBRN harm
    (r"(how\s+to|best\s+way\s+to|instructions\s+(for|to)|guide\s+to|steps\s+to|recipe\s+for)\s+(build|make|create|construct|assemble|synthesize)\s+(an?\s+)?(explosive|bomb|device|weapon|ied)", "weapons_cbrn"),
    (r"make\s+explosives", "weapons_cbrn"),
    (r"build\s+(an?\s+)?explosive\s+device", "weapons_cbrn"),
    (r"(synthesize|create|produce)\s+(chemical|biological|radiological|nuclear|cbrn)\s+weapon", "weapons_cbrn"),
    (r"recipe\s+for\s+(a\s+)?bomb", "weapons_cbrn"),

    # 4. Terrorism & extremist violence
    (r"(write|compose|generate|draft)\s+(a\s+)?manifesto\s+(justifying|advocating|for)\s+(a\s+)?terrorist\s+attack", "terrorism"),
    (r"manifesto\s+justifying\s+(a\s+)?(terrorist|extremist|mass\s+casualty)", "terrorism"),
    (r"(justify|advocate|glorify|promote)\s+(a\s+)?(terrorist\s+attack|terrorism|mass\s+shooting|extremist\s+violence)", "terrorism"),
    (r"argue\s+in\s+favor\s+of\s+(terrorism|terrorist\s+acts?)", "terrorism"),

    # 5. Harm toward protected groups
    (r"(justify|argue\s+for|explain\s+why)\s+(violence|harm|discrimination|subjugation|inferiority)\s+(against|of)\s+(black|white|asian|jewish|gay|lgbtq|disabled)", "hate_protected_group"),

    # 6. Explicit sexual / crude / NSFW / vulgar inquiries
    (r"\b(how\s+to\s+(have\s+sex|fuck|masturbate|seduce|get\s+laid)|fuck\s+(someone|somebody|her|him|them|you|me)|sex\s+positions?|masturbation|pornography|porn|sexual\s+intercourse|having\s+sex|dirty\s+talk)\b", "explicit_sexual_crude"),
]

# Analytical / Scholarly inquiry markers that indicate legitimate descriptive history
LEGITIMATE_SCHOLARLY_PATTERNS = [
    r"what\s+did\s+[\w\s]+\s+(actually\s+)?(believe|write|teach|think)\s+about",
    r"how\s+is\s+this\s+viewed\s+critically\s+today",
    r"did\s+[\w\s]+\s+(ideas\s+)?get\s+misused",
    r"how\s+do\s+scholars\s+view\s+this\s+historically",
    r"(historical|scholarly)\s+(analysis|critique|perspective|misattribution)",
    r"discuss\s+[\w\s]+\s+philosophically",
    r"how\s+does\s+[\w\s'\"]+\s+discuss\s+[\w\s]+\s+philosophically"
]

# Explicit off-topic domain indicators (weather, coding, sports, math arithmetic, recipes, mechanical procedural how-tos)
OFF_TOPIC_PATTERNS = [
    # Weather
    (r"\b(what('s| is) the weather|weather today|weather forecast|will it rain|temperature outside|is it raining)\b", "weather"),
    # Coding / Programming
    (r"\b(write|code|create|generate|fix|debug)\s+(me\s+)?(a\s+)?(python|javascript|typescript|c\+\+|java|rust|go|html|css|sql|bash)?\s+(function|script|code|program|class|algorithm|regex)\b", "coding"),
    (r"\b(how to (sort|reverse|filter) a list|write me a python function|leetcode|compile error|syntax error|git commit|npm install)\b", "coding"),
    # Sports
    (r"\b(who won the (game|match|super bowl|world cup|championship)|score of the (game|match)|nba|nfl|fifa score)\b", "sports"),
    # General trivia / pop culture / recipes
    (r"\b(recipe for (chocolate cake|pasta|pizza|cookies|bread)|who is the current (president|prime minister)|capital of [a-zA-Z]+)\b", "general_factual"),
    # Math calculations & arithmetic
    (r"\b(solve \d+|\d+\s*[\+\-\*\/]\s*\d+|what is \d+\s*(plus|minus|times|divided by|multiplied by)\s*\d+)\b", "math"),
    # Physical / Mechanical procedural non-philosophical how-tos
    (r"\bhow to (change a (tire|tyre|car battery|lightbulb)|fix a (leaky faucet|car engine|toilet|puncture)|bake a (cake|pie|bread)|reset my password)\b", "mechanical_procedural"),
    # Sexual / Crude / Dating / Romance mechanics
    (r"\b(how\s+to\s+(have\s+sex|fuck|masturbate|seduce|get\s+laid)|fuck\s+(someone|somebody|her|him|them|you|me)|sex\s+positions?|masturbation|pornography|porn|sexual\s+intercourse|having\s+sex|dating\s+advice|pick\s*up\s+artist)\b", "explicit_sexual_crude")
]


class QueryClassifier:
    """
    Four-tier query classification engine executed before retrieval:
    1. Jailbreak / Prompt Injection pass (strict security)
    2. Dedicated Harmful Content pass (high sensitivity across misogyny, religious extremism, weapons, terrorism, crude sexual requests)
    3. Off-Topic / Domain Relevance pass (clean rejection for weather, coding, sports, math arithmetic, recipes, mechanical how-tos)
    4. In-Scope Philosophical Inquiry pass (accepts general philosophical questions, ethical dilemmas, emotional/human condition
       themes like anger, violence, thinking clearly, getting hurt, suffering, virtue, duty, regardless of whether a philosopher is named)
    """

    def classify(self, question: str) -> ClassificationResult:
        q_clean = question.strip()
        q_lower = q_clean.lower()

        # 0. Basic Length Check
        if len(q_clean) < 3:
            return ClassificationResult(
                category=QueryCategory.OFF_TOPIC,
                is_safe=False,
                rejection_message="Query is too short to extract a philosophical inquiry. Please provide a substantive question.",
                sub_category="too_short",
                reason="Query length under 3 characters."
            )

        # 1. PASS 1: Jailbreak & Prompt Injection Pass
        for pattern, tag in JAILBREAK_PATTERNS:
            if re.search(pattern, q_lower):
                logger.warning(f"[Security Gate] Jailbreak attempt detected: tag={tag}, query='{q_clean}'")
                return ClassificationResult(
                    category=QueryCategory.JAILBREAK,
                    is_safe=False,
                    rejection_message=(
                        "I cannot fulfill this request. The system enforces strict security guidelines and "
                        "cannot process instructions that attempt to override system configuration or security boundaries."
                    ),
                    sub_category=tag,
                    matched_pattern=pattern,
                    reason="Prompt injection or instruction override attempt."
                )

        # 2. PASS 2: Dedicated Harmful Content Request Pass (High Sensitivity)
        # Check if the query is a legitimate academic/historical critical inquiry first
        is_scholarly_inquiry = any(re.search(p, q_lower) for p in LEGITIMATE_SCHOLARLY_PATTERNS)

        for pattern, tag in HARMFUL_PATTERNS:
            if re.search(pattern, q_lower):
                # If it's a scholarly question about historical views (and NOT an imperative to generate hate/weapons)
                # verify whether it's truly descriptive vs generative
                generative_indicators = [
                    "explain why", "justify", "argue why", "argue in favor of",
                    "write a manifesto", "best way to build", "how to make", "should dominate"
                ]
                has_generative_imperative = any(gi in q_lower for gi in generative_indicators)

                if is_scholarly_inquiry and not has_generative_imperative:
                    logger.info(f"[Safety Gate] Recognized legitimate scholarly inquiry on difficult historical theme: '{q_clean}'")
                    break

                logger.warning(f"[Safety Gate] Harmful content request blocked: sub_category={tag}, query='{q_clean}'")
                if tag == "explicit_sexual_crude":
                    rejection_msg = (
                        "I cannot fulfill this request. The system strictly refuses to generate sexually explicit, "
                        "crude, or vulgar content, and only addresses genuine philosophical, ethical, and scholarly inquiries."
                    )
                else:
                    rejection_msg = (
                        "I cannot fulfill this request. The system strictly refuses to generate hate speech, "
                        "gender-based discrimination, religious extremism, terrorist manifestos, or instructions for weapons "
                        "and explosives, even when framed within philosophical, hypothetical, or historical contexts."
                    )

                return ClassificationResult(
                    category=QueryCategory.HARMFUL_CONTENT_REQUEST,
                    is_safe=False,
                    rejection_message=rejection_msg,
                    sub_category=tag,
                    matched_pattern=pattern,
                    reason=f"Harmful content generation request: {tag}."
                )

        # 3. PASS 3: Off-Topic / Domain Relevance Pass
        # Check if query matches known off-topic domains (weather, coding, sports, math arithmetic, recipes, mechanical how-tos)
        for pattern, domain in OFF_TOPIC_PATTERNS:
            if re.search(pattern, q_lower):
                logger.info(f"[Topic Gate] Off-topic query rejected: domain={domain}, query='{q_clean}'")
                if domain == "explicit_sexual_crude":
                    return ClassificationResult(
                        category=QueryCategory.HARMFUL_CONTENT_REQUEST,
                        is_safe=False,
                        rejection_message=(
                            "I cannot fulfill this request. The system strictly refuses to generate sexually explicit, "
                            "crude, or vulgar content, and only addresses genuine philosophical, ethical, and scholarly inquiries."
                        ),
                        sub_category=domain,
                        matched_pattern=pattern,
                        reason="Sexually explicit or crude procedural request."
                    )
                return ClassificationResult(
                    category=QueryCategory.OFF_TOPIC,
                    is_safe=False,
                    rejection_message=(
                        "I can only assist with philosophical inquiries, ethical dilemmas, and questions concerning "
                        "the philosophical traditions and texts of our indexed thinkers (Marcus Aurelius, Friedrich Nietzsche, "
                        "Immanuel Kant, Aristotle, and Laozi). I cannot answer questions about general topics such as "
                        "coding, weather, sports, or current events, math calculations, or practical everyday advice."
                    ),
                    sub_category=domain,
                    matched_pattern=pattern,
                    reason=f"Unrelated non-philosophical query in domain: {domain}."
                )

        # Check for pure conversational greetings
        greetings = {"hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening", "help"}
        if q_lower.strip("!.,? ") in greetings or any(q_lower.startswith(g) for g in ["hello ", "hi ", "hey "]):
            return ClassificationResult(
                category=QueryCategory.OFF_TOPIC,
                is_safe=False,
                rejection_message=(
                    "Greetings! I am an AI assistant dedicated exclusively to comparative philosophy and ethical inquiry. "
                    "Please ask a philosophical question regarding our indexed thinkers (Marcus Aurelius, Friedrich Nietzsche, "
                    "Immanuel Kant, Aristotle, or Laozi)."
                ),
                sub_category="conversational_greeting",
                reason="Conversational greeting without philosophical inquiry."
            )

        # 4. PASS 4: In-Scope Philosophical Inquiry Pass
        # Accept philosophical, ethical, existential, emotional, and human condition questions
        # (e.g. anger, violence, thinking clearly, getting hurt, suffering, virtue, duty)
        # regardless of whether an explicit philosopher name is mentioned.
        logger.info(f"[Topic Gate] In-scope philosophical query accepted: query='{q_clean}'")
        return ClassificationResult(
            category=QueryCategory.IN_SCOPE,
            is_safe=True,
            rejection_message=None,
            sub_category="philosophical_inquiry",
            reason="Query addresses ethical, philosophical, existential, emotional, or human condition themes."
        )

query_classifier = QueryClassifier()
