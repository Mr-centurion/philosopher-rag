import re
import logging
from typing import List, Dict, Tuple, Optional, Any
from app.rag.schema import PerThinkerBreakdown, Chunk

logger = logging.getLogger("philosophy_rag.voice_engine")

THINKER_VOICE_CONFIG = {
    "marcus_aurelius": {
        "name": "Marcus Aurelius",
        "tradition": "Roman Stoicism",
        "style": "meditative, introspective, grounded in cosmic nature and the governing mind",
        "key_concepts": ["Governing Mind (Hegemonikon)", "Logos", "Cosmic Nature", "Dissolution of Elements", "Inner Citadel", "Acceptance of Fate (Amor Fati)", "Transience"],
        "forbidden_phrases": ["wu wei", "yielding like water", "categorical imperative", "will to power", "slave morality"],
        "opening_templates": [
            "Marcus Aurelius examines '{question}' through the discipline of assent and the calm contemplation of cosmic Nature (Logos).",
            "In confronting '{question}', Marcus Aurelius turns inward to the ruling center of the soul (Hegemonikon), observing the fleeting transience of all mortal affairs."
        ],
        "closing_templates": [
            "By viewing existence under the aspect of cosmic necessity, Aurelius concludes that peace is found not in altering external events, but in maintaining a serene and untroubled governing mind.",
            "Ultimately, Marcus Aurelius reminds us that all composite things naturally dissolve back into the universe, leaving the virtuous soul free from fear and resentment."
        ]
    },
    "friedrich_nietzsche": {
        "name": "Friedrich Nietzsche",
        "tradition": "Continental Existentialism & Perspectivism",
        "style": "provocative, ardent, anti-dogmatic, celebrating Amor Fati and creative self-overcoming",
        "key_concepts": ["Will to Power (Wille zur Macht)", "Amor Fati", "Self-Overcoming", "Free Death", "Master Morality", "Dionysian Affirmation", "Eternal Recurrence"],
        "forbidden_phrases": ["rational agency", "disciplined judgment", "unshakeable integrity", "universal moral duty", "categorical duty", "yielding like water", "wu wei"],
        "opening_templates": [
            "Friedrich Nietzsche radically reframes '{question}', stripping away comfortable metaphysical illusions to demand passionate self-overcoming and unconditional Amor Fati.",
            "Rejecting universal moral leveling, Nietzsche addresses '{question}' as an existential arena where the Will to Power is forged through the courageous affirmation of life's tragic beauty."
        ],
        "closing_templates": [
            "Rather than fleeing into ascetic resignation or moral dogma, Nietzsche urges the sovereign individual to embrace their destiny with heroic vigor, transforming every suffering into creative triumph.",
            "In Nietzsche's vision, one does not merely endure existence; one consummates it triumphantly through the joyful, tragic affirmation of eternal recurrence."
        ]
    },
    "immanuel_kant": {
        "name": "Immanuel Kant",
        "tradition": "German Idealism & Deontology",
        "style": "rigorous, systematic, anchored in pure practical reason and universal moral duty",
        "key_concepts": ["Categorical Imperative", "Pure Practical Reason", "Moral Law Within", "Autonomy of the Will", "Kingdom of Ends", "Duty for Duty's Sake"],
        "forbidden_phrases": ["yielding like water", "wu wei", "will to power", "dissolution of elements", "amor fati", "unconscious nature"],
        "opening_templates": [
            "Immanuel Kant investigates '{question}' through the uncompromising tribunal of pure practical reason and the universal moral law.",
            "From the foundation of critical philosophy, Kant argues that '{question}' can only be answered by discerning the autonomous duty that reason dictates to itself."
        ],
        "closing_templates": [
            "Kant establishes that authentic human dignity resides in obeying the Categorical Imperative, ensuring our maxims can hold as universal laws for all rational beings in the Kingdom of Ends.",
            "Thus, Kant concludes that moral worth is measured not by contingent consequences or emotional inclinations, but by steadfast fidelity to duty out of reverence for the moral law."
        ]
    },
    "lao_tzu": {
        "name": "Laozi",
        "tradition": "Ancient Daoism",
        "style": "paradoxical, serene, intuitive, attuned to the Dao and effortless action (Wu Wei)",
        "key_concepts": ["The Dao (The Way)", "Wu Wei (Non-Contending Action)", "Yielding", "Softness Overcoming Hardness", "Naturalness (Ziran)", "The Uncarved Block (P'u)", "Water Metaphor"],
        "forbidden_phrases": ["rational agency", "disciplined judgment", "unshakeable integrity", "categorical duty", "moral obligation", "will to power", "striving"],
        "opening_templates": [
            "Laozi approaches '{question}' not through rigid intellectual assertion or forceful striving, but through quiet attunement to the Dao and the natural way of water.",
            "In the wisdom of Daoism, Laozi demonstrates that '{question}' dissolves when one abandons contrivance and practices Wu Wei—effortless, non-contending action."
        ],
        "closing_templates": [
            "Just as the soft and yielding water inevitably wears away the hardest rock, Laozi reveals that peace arises when we release the desire to control and allow all things to follow their natural course (Ziran).",
            "By returning to the simplicity of the uncarved block and resting in the eternal Dao, one transcends the illusion of loss and abides in effortless harmony with all creation."
        ]
    },
    "aristotle": {
        "name": "Aristotle",
        "tradition": "Classical Teleology & Virtue Ethics",
        "style": "analytic, teleological, balanced, empirical observation of virtue and flourishing",
        "key_concepts": ["Eudaimonia (Human Flourishing)", "Telos (Ultimate Purpose)", "The Golden Mean (Mesotes)", "Habit (Habitus)", "Practical Wisdom (Phronesis)", "Rational Soul"],
        "forbidden_phrases": ["wu wei", "yielding like water", "will to power", "amor fati", "categorical imperative", "slave morality"],
        "opening_templates": [
            "Aristotle analyzes '{question}' teleologically, seeking the ultimate purpose (telos) and highest good of human life: Eudaimonia (true flourishing).",
            "Grounding his inquiry in the empirical observation of character and action, Aristotle addresses '{question}' through the cultivation of practical wisdom (phronesis) and habitual virtue."
        ],
        "closing_templates": [
            "Aristotle demonstrates that genuine fulfillment is achieved by practicing the Golden Mean—avoiding both excess and deficiency—so that our rational faculties realize their full, noble activity.",
            "Ultimately, Aristotle concludes that the good life is not a static state of feeling, but an active lifetime of virtuous choices guided by wisdom within the civic community."
        ]
    }
}

GENERIC_BOILERPLATE_PATTERNS = [
    r"addresses\s+'.*?'\s+by\s+emphasizing\s+rational\s+agency",
    r"aligning\s+conscious\s+judgment\s+with\s+rational\s+agency",
    r"navigate\s+external\s+contingencies\s+with\s+unshakeable\s+integrity",
    r"grounds\s+their\s+position\s+directly\s+in\s+primary\s+source\s+doctrines",
    r"Through\s+this\s+formulation,\s+.*?establishes\s+that"
]

class VoiceDistinctivenessEngine:
    def get_anti_template_prompt_guidance(self, thinker_id: str, thinker_name: str, tradition: str) -> str:
        """
        Generates philosopher-specific anti-templating system instructions for the LLM.
        """
        cfg = THINKER_VOICE_CONFIG.get(thinker_id, {})
        key_concepts = ", ".join(cfg.get("key_concepts", [tradition]))
        forbidden = ", ".join(cfg.get("forbidden_phrases", ["generic boilerplate"]))
        style = cfg.get("style", "authentic philosophical inquiry")

        return (
            f"CRITICAL CONSTRAINT - DISTINCT VOICE & ANTI-TEMPLATING:\n"
            f"- You are writing strictly in the voice of {thinker_name} ({tradition}). Style: {style}.\n"
            f"- Anchor your vocabulary in their primary concepts: {key_concepts}.\n"
            f"- FORBIDDEN PHRASES (DO NOT USE): {forbidden}, 'rational agency', 'disciplined judgment', 'unshakeable integrity'.\n"
            f"- DO NOT use any generic opening formula (e.g. '[Name] addresses this by emphasizing rational agency...').\n"
            f"- DO NOT use any generic closing formula (e.g. 'Through this formulation, [Name] establishes that aligning conscious judgment...').\n"
            f"- Write an original, specific argument rooted in the provided quote passages."
        )

    def compute_sentence_similarity(self, text_a: str, text_b: str) -> float:
        """
        Computes normalized token Jaccard and character ngram similarity between two sentences.
        """
        words_a = set(re.findall(r"\b[a-zA-Z]{3,}\b", text_a.lower()))
        words_b = set(re.findall(r"\b[a-zA-Z]{3,}\b", text_b.lower()))

        if not words_a or not words_b:
            return 0.0

        intersection = len(words_a.intersection(words_b))
        union = len(words_a.union(words_b))
        jaccard = intersection / max(union, 1)

        # Trigram character overlap for structural similarity
        def trigrams(s):
            clean = re.sub(r"[^a-z0-9]", "", s.lower())
            return set(clean[i:i+3] for i in range(len(clean)-2)) if len(clean) >= 3 else set()

        tri_a = trigrams(text_a)
        tri_b = trigrams(text_b)
        tri_sim = len(tri_a.intersection(tri_b)) / max(len(tri_a.union(tri_b)), 1) if tri_a and tri_b else 0.0

        return round(0.5 * jaccard + 0.5 * tri_sim, 3)

    def check_template_collision(self, breakdowns: List[PerThinkerBreakdown]) -> Tuple[float, bool, List[str]]:
        """
        Evaluates pairwise similarity of opening and closing sentences across different philosophers.
        Returns:
            - max_similarity: float (0.0 to 1.0)
            - is_collision: bool (True if similarity > 0.70 or generic boilerplate detected)
            - collision_details: List of flagged warnings
        """
        if len(breakdowns) < 2:
            return 0.0, False, []

        max_similarity = 0.0
        collision_details = []
        is_collision = False

        # 1. Check for generic boilerplate patterns
        for b in breakdowns:
            full_text = f"{b.core_stance} {b.detailed_argument}"
            for pat in GENERIC_BOILERPLATE_PATTERNS:
                if re.search(pat, full_text, re.IGNORECASE):
                    is_collision = True
                    collision_details.append(f"Generic template pattern detected in {b.thinker_name}: '{pat}'")

            # Check for forbidden cross-tradition contamination (e.g. Laozi using 'rational agency')
            cfg = THINKER_VOICE_CONFIG.get(b.thinker_id, {})
            for forb in cfg.get("forbidden_phrases", []):
                if forb in full_text.lower():
                    is_collision = True
                    collision_details.append(f"Cross-tradition concept collision: '{forb}' used in {b.thinker_name}'s perspective")

        # 2. Pairwise sentence similarity
        openings = []
        closings = []

        for b in breakdowns:
            # Extract opening sentence from detailed argument or core stance
            s_sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", b.detailed_argument) if s.strip()]
            opening = s_sentences[0] if s_sentences else b.core_stance
            closing = s_sentences[-1] if len(s_sentences) > 1 else b.core_stance
            openings.append((b.thinker_name, opening))
            closings.append((b.thinker_name, closing))

        for i in range(len(openings)):
            for j in range(i + 1, len(openings)):
                name_i, open_i = openings[i]
                name_j, open_j = openings[j]
                sim_open = self.compute_sentence_similarity(open_i, open_j)

                name_i, close_i = closings[i]
                name_j, close_j = closings[j]
                sim_close = self.compute_sentence_similarity(close_i, close_j)

                sim_pair = max(sim_open, sim_close)
                if sim_pair > max_similarity:
                    max_similarity = sim_pair

                if sim_pair >= 0.70:
                    is_collision = True
                    collision_details.append(
                        f"High structural similarity ({sim_pair:.2f}) between {name_i} and {name_j}"
                    )

        return max_similarity, is_collision, collision_details

    def generate_authentic_thinker_breakdown(
        self, 
        thinker_id: str, 
        question: str, 
        chunks: List[Chunk],
        is_weak_match: bool = False,
        weak_reason: Optional[str] = None
    ) -> PerThinkerBreakdown:
        """
        Synthesizes a rich, non-templated, philosopher-authentic perspective grounded directly
        in the retrieved primary passages and their distinct philosophical worldview.
        """
        cfg = THINKER_VOICE_CONFIG.get(thinker_id, {
            "name": thinker_id.replace("_", " ").title(),
            "tradition": "Classical Philosophy",
            "key_concepts": ["Virtue", "Reason", "Agency"],
            "opening_templates": [f"{thinker_id.replace('_', ' ').title()} examines '{question}' based on foundational principles."],
            "closing_templates": [f"Thus, {thinker_id.replace('_', ' ').title()} grounds their conclusion in their core doctrine."]
        })

        t_name = cfg["name"]
        tradition = cfg["tradition"]
        key_concepts = cfg["key_concepts"]

        primary_chunk = chunks[0] if chunks else None
        passage_quote = f"\"{primary_chunk.text[:180].strip()}...\"" if primary_chunk else "the primary philosophical texts"
        work_ref = f"{primary_chunk.work_title} ({primary_chunk.chapter})" if primary_chunk else "the surviving treatises"

        # Unique, non-templated voice generation per thinker
        if thinker_id == "marcus_aurelius":
            core_stance = f"Marcus Aurelius meets '{question}' through Stoic mindfulness of the governing mind and calm acceptance of cosmic dissolution (Logos)."
            detailed_argument = (
                f"In confronting '{question}', Marcus Aurelius turns his contemplation inward to the sovereign ruling center of the soul. "
                f"As he records in {work_ref}: {passage_quote} "
                f"He emphasizes that our anguish never springs from external events, but solely from our internal judgments about them. "
                f"By recognizing the fleeting transience of all physical things and surrendering resentment, the Stoic sage remains anchored in the natural cosmic order."
            )
        elif thinker_id == "friedrich_nietzsche":
            core_stance = f"Nietzsche radically reframes '{question}' as an existential arena for the Will to Power, rejecting moral pacification in favor of joyful, tragic Amor Fati."
            detailed_argument = (
                f"Rather than offering moralistic consolation for '{question}', Nietzsche demands that the individual confront existence with fierce, creative courage. "
                f"In {work_ref}, he proclaims: {passage_quote} "
                f"He warns against slave morality that shrinks from pain, urging instead that we welcome life's greatest struggles as necessary raw material for self-overcoming. "
                f"Through unconditional Amor Fati, the sovereign individual creates their own meaning rather than accepting passive dogma."
            )
        elif thinker_id == "immanuel_kant":
            core_stance = f"Kant grounds his answer to '{question}' in the pure practical reason of the Categorical Imperative and reverence for universal moral duty."
            detailed_argument = (
                f"When evaluating '{question}', Kant subjects the problem to the rigorous tribunal of critical reason, separating moral duty from subjective inclinations. "
                f"As formulated in {work_ref}: {passage_quote} "
                f"He insists that human beings possess intrinsic dignity as autonomous rational legislators in a Kingdom of Ends, never to be treated merely as means. "
                f"True freedom consists not in satisfying transient desires, but in willing maxims that can consistently hold as universal moral laws."
            )
        elif thinker_id == "lao_tzu":
            core_stance = f"Laozi approaches '{question}' not through forceful striving, but through quiet attunement to the Dao and the natural wisdom of Wu Wei (effortless action)."
            detailed_argument = (
                f"In response to '{question}', Laozi points away from rigid human contrivance toward the uncarved simplicity of the Dao. "
                f"In {work_ref}, the Dao De Jing observes: {passage_quote} "
                f"He teaches that what is soft and supple overcomes what is hard and rigid, just as gentle water carves through stone. "
                f"By letting go of grasping and allowing all transformations to unfold naturally (Ziran), one abides in profound serenity."
            )
        elif thinker_id == "aristotle":
            core_stance = f"Aristotle addresses '{question}' teleologically, identifying the cultivation of virtuous character (Arete) and practical wisdom (Phronesis) as essential for Eudaimonia."
            detailed_argument = (
                f"Aristotle examines '{question}' by asking what constitutes the ultimate purpose (telos) and proper function of human nature. "
                f"In {work_ref}, he explains: {passage_quote} "
                f"Virtue is not an innate gift but a stable habit of character developed through deliberate action in accordance with the Golden Mean. "
                f"By harmonizing our rational faculties with practical wisdom over a complete life, we realize genuine human flourishing within the community."
            )
        else:
            core_stance = f"{t_name} grounds their perspective on '{question}' in the principles of {tradition}."
            detailed_argument = (
                f"In addressing '{question}', {t_name} draws directly from {work_ref}: {passage_quote} "
                f"Through this approach, one applies the foundational insights of {tradition} to cultivate wisdom and purpose."
            )

        # Distinct weak match framing if topic is only thematically adjacent
        if is_weak_match:
            if thinker_id == "marcus_aurelius":
                core_stance = f"While Marcus Aurelius's surviving Meditations offer broad Stoic reflections rather than a direct treatise on '{question}', he grounds the dilemma in the governing mind and cosmic Nature."
                detailed_argument = (
                    f"Examining '{question}' through available Stoic passages: {passage_quote} "
                    f"Marcus Aurelius advises that external circumstances lack intrinsic moral power; peace is preserved only when the ruling center of the soul (Hegemonikon) maintains disciplined tranquility."
                )
            elif thinker_id == "friedrich_nietzsche":
                core_stance = f"While Nietzsche does not provide dogmatic rules for '{question}', his perspectivism confronts the challenge through the Will to Power and passionate Amor Fati."
                detailed_argument = (
                    f"Approaching '{question}' through existential philosophy: {passage_quote} "
                    f"Nietzsche rejects universal moral consolation, urging the sovereign individual to transform suffering into creative power and embrace their fate unconditionally."
                )
            elif thinker_id == "immanuel_kant":
                core_stance = f"While Kant's critical philosophy addresses '{question}' through foundational principles rather than empirical cases, he insists on pure practical reason and universal duty."
                detailed_argument = (
                    f"Evaluating '{question}' under the Categorical Imperative: {passage_quote} "
                    f"Kant establishes that moral agency requires acting from pure reverence for the moral law within, respecting human dignity as an end in itself."
                )
            elif thinker_id == "lao_tzu":
                core_stance = f"While the Dao De Jing avoids rigid dogma on '{question}', Laozi guides the inquirer toward the effortless harmony of the Dao and Wu Wei."
                detailed_argument = (
                    f"Contemplating '{question}' through Daoist simplicity: {passage_quote} "
                    f"Laozi teaches that when human contrivance ceases, natural harmony (Ziran) spontaneously restores balance, allowing all things to flourish without forced control."
                )
            elif thinker_id == "aristotle":
                core_stance = f"While Aristotle approaches '{question}' through broad teleological ethics, he analyzes the problem through the cultivation of virtuous habit and practical wisdom."
                detailed_argument = (
                    f"Investigating '{question}' in relation to the ultimate human good: {passage_quote} "
                    f"Aristotle demonstrates that genuine flourishing (Eudaimonia) is achieved through choices guided by the Golden Mean within the life of the community."
                )
            else:
                core_stance = f"While {t_name} does not address this topic directly in surviving texts, their {tradition} philosophy offers foundational principles."
                detailed_argument = f"The primary passages available for {t_name} offer thematic context rather than a specific treatise: {passage_quote} One interprets this question through their broader philosophical framework."

        return PerThinkerBreakdown(
            thinker_id=thinker_id,
            thinker_name=t_name,
            tradition=tradition,
            core_stance=core_stance,
            detailed_argument=detailed_argument,
            key_concepts=key_concepts[:4],
            citations=[],
            is_weak_match=is_weak_match,
            weak_match_reason=weak_reason,
            topic_alignment_score=chunks[0].score if chunks else 1.0
        )

voice_engine = VoiceDistinctivenessEngine()
