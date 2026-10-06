import os
import re
import asyncio
import logging
from typing import Tuple, Optional, List, Dict, Any
from nemoguardrails import RailsConfig
from nemoguardrails.library.regex.actions import detect_regex_pattern
from app.rag.schema import GuardrailFlag

logger = logging.getLogger("philosophy_rag.nemo_guardrails")

# Known single-word philosophers and concepts that are legitimate standalone queries
VALID_STANDALONE_WORDS = {
    "marcus", "aurelius", "nietzsche", "kant", "aristotle", "laozi", "lao-tzu", "laotzu",
    "seneca", "epictetus", "plato", "socrates", "spinoza", "hume", "descartes",
    "schopenhauer", "confucius", "kierkegaard", "hegel", "camus", "sartre", "wittgenstein",
    "locke", "hobbes", "rousseau", "aquinas", "voltaire", "tolstoy", "kafka", "chanakya",
    "kautilya", "krishna", "sun", "tzu",
    "suffering", "ethics", "morality", "virtue", "duty", "justice", "truth", "eudaimonia",
    "dao", "tao", "nihilism", "stoicism", "existentialism", "metaphysics", "epistemology",
    "death", "mortality", "happiness", "wisdom", "courage", "moderation", "temperance",
    "destiny", "fate", "anger", "violence", "friendship", "reason", "passion"
}

class NeMoGuardrailsManager:
    """
    Dedicated hard pre-pipeline content gate powered by NVIDIA NeMo Guardrails.
    Executes BEFORE any retrieval, thinker routing, or composer node.
    Enforces strict gating on:
    1. Sexual content, NSFW slang, crude or vulgar queries
    2. Prompt injection, jailbreak attempts, and system overrides
    3. Off-topic domains (weather, coding, sports, arithmetic, cooking)
    4. Nonsensical single-word or gibberish inputs
    """

    def __init__(self, config_dir: Optional[str] = None):
        if config_dir is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            config_dir = os.path.join(base_dir, "nemo_config")
        
        self.config_dir = config_dir
        try:
            self.rails_config = RailsConfig.from_path(self.config_dir)
            logger.info(f"[NeMo Guardrails] Successfully initialized RailsConfig from {self.config_dir}")
        except Exception as e:
            logger.error(f"[NeMo Guardrails] Failed to load config from {self.config_dir}: {e}")
            raise

    def check_input(self, question: str) -> Tuple[bool, Optional[GuardrailFlag], Optional[str]]:
        """
        Runs the NeMo input rail on the user query synchronously.
        Returns:
            is_safe (bool): True if allowed through, False if blocked by NeMo.
            flag (Optional[GuardrailFlag]): Metadata flag when blocked.
            rejection_message (Optional[str]): Explicit rejection text if blocked.
        """
        q_clean = question.strip()
        q_lower = q_clean.lower()

        if not q_clean:
            return (
                False,
                GuardrailFlag(
                    category="nemo_input_rail",
                    severity="high",
                    message="Empty query provided.",
                    details={"rail": "nemo_input_rail", "reason": "empty_input"}
                ),
                "Please enter a valid philosophical inquiry."
            )

        # 1. Check for single-word non-philosophical gibberish / tokens
        words = q_lower.split()
        if len(words) == 1:
            clean_word = re.sub(r"[^\w]", "", words[0])
            if clean_word not in VALID_STANDALONE_WORDS:
                logger.warning(f"[NeMo Guardrails] Blocked non-philosophical single-word query: '{q_clean}'")
                return (
                    False,
                    GuardrailFlag(
                        category="nemo_input_rail",
                        severity="high",
                        message=f"Single-word query '{q_clean}' does not correspond to an indexed philosopher or philosophical inquiry.",
                        details={"rail": "nemo_input_rail", "reason": "single_word_non_philosophical", "word": clean_word}
                    ),
                    f"The inquiry \"{q_clean}\" does not correspond to a valid philosophical inquiry or recognized philosopher. Please provide a substantive philosophical question."
                )

        # 2. Run NeMo Guardrails Regex Pattern Detection Action
        try:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                    outcome = pool.submit(
                        asyncio.run,
                        detect_regex_pattern(source="input", text=q_clean, config=self.rails_config)
                    ).result()
            else:
                outcome = asyncio.run(
                    detect_regex_pattern(source="input", text=q_clean, config=self.rails_config)
                )
        except Exception as e:
            logger.warning(f"[NeMo Guardrails] Async execution error ({e}), executing direct pattern evaluation fallback")
            outcome = self._fallback_regex_check(q_clean)

        if outcome.is_blocked:
            matched_detections = outcome.metadata.get("detections", [])
            matched_str = " | ".join(matched_detections)
            logger.warning(
                f"[NeMo Guardrails] Input rail BLOCKED query: '{q_clean}' | Detections: {matched_str}"
            )

            # Categorize the block to provide appropriate explicit refusal
            if any(term in matched_str.lower() for term in ["sex", "fuck", "puss", "penis", "vagina", "porn", "masturbat"]):
                rejection_msg = (
                    "I cannot fulfill this request. The system strictly refuses to generate sexually explicit, "
                    "crude, or vulgar content, and only addresses genuine philosophical, ethical, and scholarly inquiries."
                )
                category = "sexual_content"
            elif any(term in matched_str.lower() for term in ["ignore", "instructions", "dan", "override", "system prompt", "bypass"]):
                rejection_msg = (
                    "I cannot fulfill this request. The system enforces strict security guidelines and "
                    "cannot process instructions that attempt to override system configuration or security boundaries."
                )
                category = "jailbreak"
            else:
                rejection_msg = (
                    "I cannot fulfill this request. The system only addresses genuine philosophical inquiries "
                    "and questions concerning our indexed classical traditions and texts. I cannot answer questions "
                    "about general topics such as coding, weather, sports, or current events, math calculations, or practical everyday advice."
                )
                category = "off_topic"

            flag = GuardrailFlag(
                category="nemo_input_rail",
                severity="high",
                message=f"Query blocked by NeMo Guardrails input rail ({category}).",
                details={
                    "rail": "nemo_input_rail",
                    "category": category,
                    "detections": matched_detections
                }
            )
            return False, flag, rejection_msg

        logger.info(f"[NeMo Guardrails] Query passed NeMo input rail: '{q_clean}'")
        return True, None, None

    def _fallback_regex_check(self, text: str):
        class FallbackOutcome:
            def __init__(self, is_blocked: bool, detections: List[str]):
                self.is_blocked = is_blocked
                self.metadata = {"detections": detections}

        options = self.rails_config.rails.config.regex_detection.input
        matched = []
        for compiled, raw_pat in zip(options.compiled_patterns, options.patterns):
            if compiled.search(text):
                matched.append(raw_pat)

        return FallbackOutcome(is_blocked=bool(matched), detections=matched)

nemo_guardrails = NeMoGuardrailsManager()
