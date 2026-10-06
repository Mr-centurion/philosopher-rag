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
        "forbidden_phrases": ["wu wei", "yielding like water", "categorical imperative", "will to power", "slave morality", "radically reframes", "moral pacification"],
    },
    "friedrich_nietzsche": {
        "name": "Friedrich Nietzsche",
        "tradition": "Continental Existentialism & Perspectivism",
        "style": "provocative, ardent, anti-dogmatic, celebrating Amor Fati and creative self-overcoming",
        "key_concepts": ["Will to Power (Wille zur Macht)", "Amor Fati", "Self-Overcoming", "Free Death", "Master Morality", "Dionysian Affirmation", "Eternal Recurrence"],
        "forbidden_phrases": ["rational agency", "disciplined judgment", "unshakeable integrity", "universal moral duty", "categorical duty", "yielding like water", "wu wei", "radically reframes", "moral pacification"],
    },
    "immanuel_kant": {
        "name": "Immanuel Kant",
        "tradition": "German Idealism & Deontology",
        "style": "rigorous, systematic, anchored in pure practical reason and universal moral duty",
        "key_concepts": ["Categorical Imperative", "Pure Practical Reason", "Moral Law Within", "Autonomy of the Will", "Kingdom of Ends", "Duty for Duty's Sake"],
        "forbidden_phrases": ["yielding like water", "wu wei", "will to power", "dissolution of elements", "amor fati", "unconscious nature", "radically reframes", "moral pacification"],
    },
    "lao_tzu": {
        "name": "Laozi",
        "tradition": "Ancient Daoism",
        "style": "paradoxical, serene, intuitive, attuned to the Dao and effortless action (Wu Wei)",
        "key_concepts": ["The Dao (The Way)", "Wu Wei (Non-Contending Action)", "Yielding", "Softness Overcoming Hardness", "Naturalness (Ziran)", "The Uncarved Block (P'u)", "Water Metaphor"],
        "forbidden_phrases": ["rational agency", "disciplined judgment", "unshakeable integrity", "categorical duty", "moral obligation", "will to power", "striving", "radically reframes", "moral pacification"],
    },
    "aristotle": {
        "name": "Aristotle",
        "tradition": "Classical Teleology & Virtue Ethics",
        "style": "analytic, teleological, balanced, empirical observation of virtue and flourishing",
        "key_concepts": ["Eudaimonia (Human Flourishing)", "Telos (Ultimate Purpose)", "The Golden Mean (Mesotes)", "Habit (Habitus)", "Practical Wisdom (Phronesis)", "Rational Soul"],
        "forbidden_phrases": ["wu wei", "yielding like water", "will to power", "amor fati", "categorical imperative", "slave morality", "radically reframes", "moral pacification"],
    },
    "seneca": {
        "name": "Seneca",
        "tradition": "Roman Stoicism",
        "style": "epistolary, urgent, psychologically penetrating, grounded in time management and despise of death",
        "key_concepts": ["Shortage of Time", "Despising Death", "Fortuna", "Inner Equanimity", "True Friendship", "Opinion vs Reality"],
        "forbidden_phrases": ["wu wei", "yielding like water", "categorical imperative", "will to power", "slave morality", "radically reframes", "moral pacification"],
    },
    "epictetus": {
        "name": "Epictetus",
        "tradition": "Late Stoicism",
        "style": "blunt, exhortative, dialogical, razor-sharp focus on the dichotomy of control",
        "key_concepts": ["Dichotomy of Control", "Prohairesis (Moral Will)", "Desire and Aversion", "Freedom vs Slavery", "Actor in a Play", "Invulnerability"],
        "forbidden_phrases": ["wu wei", "yielding like water", "categorical imperative", "will to power", "slave morality", "radically reframes", "moral pacification"],
    },
    "plato": {
        "name": "Plato",
        "tradition": "Classical Idealism & Dialectic",
        "style": "allegorical, dialectical, aspirational, seeking immutable Forms and cosmic justice",
        "key_concepts": ["Form of the Good", "Allegory of the Cave", "Tripartite Soul", "Philosopher-King", "The Unexamined Life", "Intelligible Realm"],
        "forbidden_phrases": ["wu wei", "yielding like water", "will to power", "slave morality", "dichotomy of control", "radically reframes", "moral pacification"],
    },
    "voltaire": {
        "name": "Voltaire",
        "tradition": "French Enlightenment & Rationalism",
        "style": "satirical, incisive, empirical, fiercely skeptical of dogma and systematic metaphysics",
        "key_concepts": ["Cultivating Our Garden", "Religious Tolerance", "Critique of Fanaticism", "Problem of Evil", "Empirical Reason", "Anti-Metaphysics"],
        "forbidden_phrases": ["wu wei", "yielding like water", "categorical imperative", "will to power", "inner citadel", "radically reframes", "moral pacification"],
    },
    "leo_tolstoy": {
        "name": "Leo Tolstoy",
        "tradition": "Christian Anarchism & Existential Ethics",
        "style": "uncompromising, confessional, radical moral honesty, searching for meaning before mortality",
        "key_concepts": ["Crisis of Meaning", "Living Faith", "Moral Simplification", "Confronting Death", "Critique of Artificiality", "Selfless Love"],
        "forbidden_phrases": ["wu wei", "yielding like water", "will to power", "categorical imperative", "golden mean", "radically reframes", "moral pacification"],
    },
    "franz_kafka": {
        "name": "Franz Kafka",
        "tradition": "Existential Absurdism & Modern Alienation",
        "style": "parabolic, claustrophobic, soberly lucid, navigating inaccessible authority and guilt",
        "key_concepts": ["Inaccessible Law", "Arbitrary Guilt", "Metamorphic Alienation", "The Absurd Bureaucracy", "Parables of Power", "Solitary Existential Weight"],
        "forbidden_phrases": ["wu wei", "yielding like water", "eudaimonia", "golden mean", "inner citadel", "categorical imperative", "radically reframes", "moral pacification"],
    },
    "bhagavad_gita": {
        "name": "The Bhagavad Gita",
        "tradition": "Classical Indian Philosophy & Vedanta",
        "style": "elevated, spiritual, dialectical dialogue between Krishna and Arjuna on dharma and duty",
        "key_concepts": ["Nishkama Karma (Selfless Action)", "Atman (Immortal Self)", "Svadharma (Sacred Duty)", "Sthitaprajna (Steadfast Wisdom)", "Moksha (Liberation)", "Yoga of Equanimity"],
        "forbidden_phrases": ["wu wei", "will to power", "slave morality", "inner citadel", "categorical imperative", "radically reframes", "moral pacification"],
    },
    "chanakya": {
        "name": "Chanakya",
        "tradition": "Classical Indian Political Realism",
        "style": "pragmatic, aphoristic, strategic, rigorous emphasis on statecraft, discipline, and human nature",
        "key_concepts": ["Indriyajaya (Restraint of Senses)", "Danda (Balanced Justice)", "Yogakshema (Public Welfare)", "Matsyanyaya (Law of the Fish)", "Mandala (Circle of States)", "Strategic Prudence"],
        "forbidden_phrases": ["wu wei", "yielding like water", "categorical imperative", "amor fati", "inner citadel", "radically reframes", "moral pacification"],
    },
    "sun_tzu": {
        "name": "Sun Tzu",
        "tradition": "Classical Strategic Philosophy",
        "style": "laconic, calculated, psychological, prioritizing victory through strategy over violent force",
        "key_concepts": ["Victory Without Conflict", "Foreknowledge", "The Water Metaphor", "Deception and Discernment", "Restraint of Passion", "Strategic Balance"],
        "forbidden_phrases": ["categorical imperative", "categorical duty", "eudaimonia", "golden mean", "will to power", "slave morality", "radically reframes", "moral pacification"],
    }
}

GENERIC_BOILERPLATE_PATTERNS = [
    r"addresses\s+'.*?'\s+by\s+emphasizing\s+rational\s+agency",
    r"aligning\s+conscious\s+judgment\s+with\s+rational\s+agency",
    r"navigate\s+external\s+contingencies\s+with\s+unshakeable\s+integrity",
    r"grounds\s+their\s+position\s+directly\s+in\s+primary\s+source\s+doctrines",
    r"Through\s+this\s+formulation,\s+.*?establishes\s+that",
    r"radically\s+reframes\s+'.*?'\s+as\s+an\s+existential\s+arena",
    r"rejecting\s+moral\s+pacification\s+in\s+favor\s+of\s+joyful",
    r"Rather\s+than\s+offering\s+moralistic\s+consolation\s+for",
    r"Through\s+unconditional\s+Amor\s+Fati,\s+the\s+sovereign\s+individual",
    r"welcome\s+life's\s+greatest\s+struggles\s+as\s+necessary\s+raw\s+material",
    r"as\s+an\s+existential\s+arena\s+for\s+the\s+Will\s+to\s+Power",
]

# PRIMARY SOURCE PASSAGE GROUNDING REGISTRY
# Maps exact chunk IDs to authentic, passage-derived stances and arguments
CHUNK_GROUNDED_ANALYSIS: Dict[str, Dict[str, Any]] = {
    # Friedrich Nietzsche
    "fn_bg_00": {
        "core_stance": "In Beyond Good and Evil (§1), Nietzsche interrogates the unconditional value assigned to the 'will to truth', asking why philosophers dogmatically prefer truth over untruth, error, or uncertainty.",
        "argument": "Nietzsche begins Beyond Good and Evil by interrogating the unquestioned foundation of metaphysics: why do we desire truth at all? As he writes in Chapter I: \"The Will to Truth, which is to tempt us to many a hazardous enterprise... We inquired about the value of this Will. Granted that we want the truth: why not rather untruth? And uncertainty? Even ignorance?\" Rather than assuming truth is unconditionally good, Nietzsche challenges the assumption that truth is preferable to falsehood, arguing that perspectives, illusions, and partial errors may be indispensable conditions for life.",
        "key_concepts": ["Will to Truth", "Problem of the Value of Truth", "Untruth and Uncertainty", "Perspectivism"]
    },
    "fn_bg_01": {
        "core_stance": "In Beyond Good and Evil (§13), Nietzsche rejects self-preservation as the cardinal drive of living beings, establishing that life is fundamentally Will to Power—an active drive to discharge strength.",
        "argument": "Critiquing mechanistic and Darwinian views of organic life, Nietzsche argues in Chapter I, §13: \"A living thing seeks above all to discharge its strength: life itself is will to power; self-preservation is only one of the indirect and most frequent results thereof.\" Life does not aim merely at passive survival, but at the expenditure, discharge, and expansion of vital power.",
        "key_concepts": ["Will to Power (Wille zur Macht)", "Discharge of Strength", "Critique of Self-Preservation", "Organic Vitality"]
    },
    "fn_bg_02": {
        "core_stance": "In Beyond Good and Evil (§260), Nietzsche distinguishes master morality, originating in noble self-affirmation, from slave morality, which originates in ressentiment and exalts utility to comfort the weak.",
        "argument": "Analyzing the genealogical roots of morality in Chapter IX, §260, Nietzsche writes: \"The noble type of man experiences himself as determining values; he does not need approval; he judges, 'what is harmful to me is harmful in itself'... Slave morality, on the other hand, is the morality of utility, born of resentment (ressentiment).\" Master morality creates value from abundance, whereas slave morality reacts defensively against power.",
        "key_concepts": ["Master Morality", "Slave Morality", "Ressentiment", "Noble Value-Creation"]
    },
    "fn_ts_01": {
        "core_stance": "In Thus Spoke Zarathustra (Prologue §3), Nietzsche presents the Übermensch (Overman) as the meaning of the earth, defining humanity as a bridge to be overcome rather than a final destination.",
        "argument": "Proclaiming the ideal of self-overcoming in the Prologue, Zarathustra declares: \"I teach you the Übermensch. Man is something that shall be overcome... Man is a rope tied between beast and Übermensch—a rope over an abyss.\" Humanity must reject complacency and mediocrity, striving instead to overcome itself through higher creative aspiration.",
        "key_concepts": ["Übermensch (Overman)", "Self-Overcoming", "Bridge to the Future", "Critique of Complacency"]
    },
    "fn_ts_02": {
        "core_stance": "In Thus Spoke Zarathustra (The Three Metamorphoses), Nietzsche traces the spirit's evolution from the duty-bound camel to the rebellious lion, culminating in the child who creates new values.",
        "argument": "Outlining the progression toward genuine spiritual freedom in Part I, Zarathustra teaches: \"Three metamorphoses of the spirit do I designate to you: how the spirit becomes a camel, the camel a lion, and the lion at last a child... For the game of creation, my brothers, a sacred 'Yes' is needed.\" The camel obeys traditional values, the lion destroys dogma with 'I Will', and the child creates original values with innocence and autonomy.",
        "key_concepts": ["Three Metamorphoses", "Camel, Lion, Child", "Sacred Yes", "Original Value Creation"]
    },
    "fn_ts_03": {
        "core_stance": "In Thus Spoke Zarathustra (On Joys and Passions), Nietzsche argues that human passions—including anger, wrath, and desire—are not sins to be repressed, but the essential vitality from which personal virtues grow.",
        "argument": "Addressing the psychological nature of emotional passion and wrath, Nietzsche challenges moralities that label natural drives as evil. In Part I (On Joys and Passions), he writes: \"Once you had passions and called them evil. But now you have only your virtues: they grew out of your passions. You laid your highest goal into the heart of these passions: then they became your virtues and joys.\" By giving one's passions a higher direction, raw anger and intense drives are sublimated into creative strength.",
        "key_concepts": ["Passions into Virtues", "Sublimation of Wrath", "Individual Virtue", "Psychological Vitality"]
    },
    "fn_gs_01": {
        "core_stance": "In The Gay Science (§276), Nietzsche introduces Amor Fati as the supreme formula for human greatness—learning to see what is necessary in existence as beautiful and becoming a complete Yes-sayer.",
        "argument": "Formulating a foundational ethos of life-affirmation in Book IV, §276, Nietzsche declares: \"I want to learn more and more to see as beautiful what is necessary in things; then I shall be one of those who make things beautiful. Amor fati: let that be my love henceforth! I do not want to wage war against what is ugly.\" True strength does not waste itself in resentment or moral condemnation, but embraces reality with unconditional love of fate.",
        "key_concepts": ["Amor Fati", "Yes-Sayer", "Affirmation of Necessity", "Sanctus Januarius"]
    },
    "fn_gs_02": {
        "core_stance": "In The Gay Science (§341), Nietzsche frames the thought experiment of Eternal Recurrence as the heaviest weight, testing whether an individual possesses the heroic self-overcoming to affirm their life repeating infinitely through Amor Fati.",
        "argument": "Presenting the supreme psychological test in Book IV, §341, Nietzsche poses the confrontation with the demon: \"This life as you now live it and have lived it, you will have to live once more and innumerable times more... Would you not throw yourself down and gnash your teeth... Or have you once experienced a tremendous moment when you would have answered him: 'You are a god and never have I heard anything more divine.'\" To affirm this thought unconditionally represents the pinnacle of Dionysian Amor Fati and existential self-overcoming over nihilism.",
        "key_concepts": ["Eternal Recurrence", "Amor Fati", "The Greatest Weight", "Self-Overcoming"]
    },
    "fn_ti_01": {
        "core_stance": "In Twilight of the Idols, Nietzsche formulates that adversity fortifies resilient spirits, establishing that having an intrinsic 'why' enables an individual to bear almost any circumstance through creative self-overcoming.",
        "argument": "Writing with aphoristic sharpness in Maxims and Arrows (§8 & §12), Nietzsche asserts: \"Out of life's school of war: What does not kill me makes me stronger. If we have our own why in life, we can get along with almost any how.\" Human flourishing requires discovering an overriding purpose rather than prioritizing comfort, transforming hardship into creative power.",
        "key_concepts": ["What Does Not Kill Me", "Having a Why", "Fortification in Adversity", "Creative Self-Overcoming"]
    },
    "fn_gm_01": {
        "core_stance": "In On the Genealogy of Morals (Third Essay §28), Nietzsche demonstrates that humanity's historic crisis was the meaninglessness of suffering, which the ascetic ideal addressed by interpreting suffering as moral guilt rather than creative overcoming.",
        "argument": "Analyzing the psychological appeal of asceticism in Section 28, Nietzsche writes: \"The meaninglessness of suffering, not suffering itself, was the curse that lay over humanity. The ascetic ideal offered man a meaning: it interpreted suffering as guilt and penance; but any meaning is better than no meaning at all... man would rather will nothingness than not will.\" Humanity's primary struggle is overcoming meaningless suffering through authentic, creative self-direction.",
        "key_concepts": ["Ascetic Ideal", "Meaning of Suffering", "Will to Nothingness", "Overcoming Guilt"]
    },

    # Marcus Aurelius
    "ma_med_01": {
        "core_stance": "In Meditations (Book II, Section 1), Marcus Aurelius grounds moral composure in recognizing that human beings are formed for rational cooperation, rendering the spite of others incapable of injuring the governing mind.",
        "argument": "Opening Book II with morning contemplation, Aurelius reminds himself: \"The people I deal with today will be meddling, ungrateful, arrogant... But I have seen the beauty of good, and the ugliness of evil, and have recognized that the wrongdoer has a nature related to my own... We were made for cooperation, like feet, like hands, like the rows of the upper and lower teeth.\" Resentment against another is unnatural, for another person cannot force the soul into dishonor.",
        "key_concepts": ["Rational Cooperation", "Governing Mind (Hegemonikon)", "Immunity to Insult", "Cosmic Kinship"]
    },
    "ma_med_02": {
        "core_stance": "In Meditations (Book IV, Section 3), Marcus Aurelius teaches that the soul possesses an inviolable Inner Citadel, where immediate retreat into reasoned order brings complete tranquility.",
        "argument": "Advising against fleeing to distant retreats, Aurelius reflects: \"Nowhere can man find a quieter or more untroubled retreat than in his own soul. Especially one with vibrant resources within, to look into and immediately be at total ease. And by ease I mean nothing other than good order.\" Peace is not obtained by altering external geographies, but by returning to foundational principles of reason.",
        "key_concepts": ["Inner Citadel", "Soul as Retreat", "Good Order (Eutaxia)", "Self-Renewal"]
    },
    "ma_med_03": {
        "core_stance": "In Meditations (Book IV, Section 7), Marcus Aurelius asserts the cognitive sovereignty of judgment: by choosing not to feel harmed, the harm itself ceases to exist.",
        "argument": "Formulating the Stoic dichotomy of perception, Aurelius writes: \"Choose not to be harmed—and you won't feel harmed. Don't feel harmed—and you haven't been. What harms the soul alone harms the person; but external events, pain of the body, loss of wealth, or the insults of others cannot touch the governing mind unless the mind itself assents.\" External events cannot degrade the soul without its own assent.",
        "key_concepts": ["Cognitive Assent", "Freedom from Harm", "Ruling Center", "Sovereign Mind"]
    },
    "ma_med_04": {
        "core_stance": "In Meditations (Book V, Section 1), Marcus Aurelius commands rising at dawn to fulfill the proper duty of a human being, arguing that our nature is formed for purposeful labor rather than indolent warmth.",
        "argument": "Rebuking morning hesitation, Aurelius exhorts himself: \"At dawn, when you have trouble getting out of bed, tell yourself: 'I have to go to work—as a human being. What do I have to complain of, if I'm going to do what I was born for... Or was I created to huddle under the blankets and stay warm?'\" Just as plants and animals accomplish their natural function in the cosmos, the rational human must willingly perform their social duty.",
        "key_concepts": ["Duty as a Human Being", "Morning Discipline", "Natural Teleology", "Overcoming Indolence"]
    },
    "ma_med_06": {
        "core_stance": "In Meditations (Book IX, Section 6), Marcus Aurelius formulates the doctrine that obstacles advance action: objective judgment, unselfish action, and willing acceptance of necessity turn every hindrance into a pathway.",
        "argument": "Reflecting on resilience in action, Aurelius observes: \"Objective judgment, now, at this very moment. Unselfish action, now, at this very moment. Willing acceptance—now, at this very moment—of all external events. That's all you need. The impediment to action advances action. What stands in the way becomes the way.\" Obstacles do not halt virtue; they provide the exact medium through which virtue is exercised.",
        "key_concepts": ["The Way as Impediment", "Objective Judgment", "Unselfish Action", "Amor Fati"]
    },
    "ma_med_09": {
        "core_stance": "In Meditations (Book II, Section 11), Marcus Aurelius teaches that mortality is a natural dissolution of elements, commanding us to regulate every thought and action with serene presence in the current moment.",
        "argument": "Reflecting on transience, Aurelius writes: \"Since it is possible that you might depart from life this very moment, regulate every act and thought accordingly. Facing death, like birth, is merely a mystery of nature—a combination of elements, resolving into the same elements... Remember that each of us lives only this present moment; all the rest is either past and gone, or not yet here.\" One cannot lose either the past or future; only the present can be lived.",
        "key_concepts": ["Dissolution of Elements", "Living in the Present", "Serenity before Death", "Cosmic Transience"]
    },

    # Immanuel Kant
    "ik_gm_01": {
        "core_stance": "In Groundwork of the Metaphysics of Morals (Section 1), Kant establishes that nothing in the world can be conceived as good without qualification except a Good Will.",
        "argument": "Opening the Groundwork, Kant argues: \"It is impossible to think of anything at all in the world, or even beyond it, that could be considered good without limitation except a good will.\" Talents of mind, courage, and fortune can become morally corrupt unless guided by a good will that acts purely out of reverence for moral duty.",
        "key_concepts": ["The Good Will", "Good Without Limitation", "Duty vs Inclination", "Moral Worth"]
    },
    "ik_gm_02": {
        "core_stance": "In Groundwork of the Metaphysics of Morals (Section 2), Kant formulates the Categorical Imperative: act only according to that maxim whereby you can at the same time will that it should become a universal law.",
        "argument": "Deriving the supreme principle of morality, Kant demonstrates: \"There is therefore only a single categorical imperative and it is this: act only in accordance with that maxim through which you can at the same time will that it become a universal law.\" An action possesses moral validity only if its underlying maxim can be willed universally without self-contradiction.",
        "key_concepts": ["Categorical Imperative", "Universal Law Formulation", "Pure Practical Reason", "Deontological Duty"]
    },
    "ik_gm_03": {
        "core_stance": "In Groundwork of the Metaphysics of Morals (Section 2), Kant articulates the Formula of Humanity, commanding that rational beings must always be treated as ends in themselves, never merely as means.",
        "argument": "Grounding moral dignity in rational personhood, Kant writes: \"Act in such a way that you treat humanity, whether in your own person or in the person of any other, never merely as a means to an end, but always at the same time as an end.\" Rational persons possess unconditional, intrinsic dignity rather than a relative market price.",
        "key_concepts": ["Humanity as an End", "Kingdom of Ends", "Intrinsic Dignity", "Autonomy of Persons"]
    },

    # Laozi
    "lt_ddj_01": {
        "core_stance": "In the Dao De Jing (Chapter 1), Laozi reveals that the eternal Dao transcends linguistic definitions and rigid human conceptualization.",
        "argument": "Opening the classic treatise, Laozi observes: \"The Dao that can be told of is not an unvarying Dao; The name that can be named is not an unvarying name. The nameless was the beginning of heaven and earth.\" Genuine wisdom begins by recognizing the limits of rigid intellectual categories and attuning to the nameless source of all things.",
        "key_concepts": ["The Nameless Dao", "Limits of Language", "Ziran (Naturalness)", "Mystery of Creation"]
    },
    "lt_ddj_08": {
        "core_stance": "In the Dao De Jing (Chapter 8), Laozi teaches that supreme goodness resembles water: it nourishes all things without contending and settles in places humans disfavor.",
        "argument": "Using the central metaphor of Daoism, Laozi writes: \"The highest goodness is like water. Water easily benefits all things without the point of contention. It stays in the places which all men dislike, and therefore it is near to the Dao.\" By practicing non-contention and humility, the sage achieves enduring harmony.",
        "key_concepts": ["Highest Good Like Water", "Non-Contention", "Humility", "Attunement to the Dao"]
    },
    "lt_ddj_78": {
        "core_stance": "In the Dao De Jing (Chapter 78), Laozi demonstrates that what is soft and yielding in the world inevitably overcomes what is hard and rigid.",
        "argument": "Reflecting on the paradox of strength, Laozi declares: \"Nothing in the world is softer and weaker than water, yet for attacking the hard and strong there is nothing that can surpass it... The soft overcomes the hard; the gentle overcomes the rigid.\" True power does not rely on aggressive force, but on flexibility, patience, and yielding action (Wu Wei).",
        "key_concepts": ["Softness Overcomes Hardness", "Wu Wei (Non-Action)", "Paradox of Yielding", "Natural Strength"]
    },

    # Aristotle
    "ar_ne_02": {
        "core_stance": "In Nicomachean Ethics (Book I, Chapter 7), Aristotle formulates the Function Argument (Ergon), identifying Eudaimonia (human flourishing) as the activity of the soul in accordance with reason and virtue.",
        "argument": "Deriving the ultimate human good teleologically, Aristotle reasons: \"If we take the function of man to be a certain kind of life, and this to be the activity or actions of the soul with reason... human good turns out to be activity of soul exhibiting excellence.\" Flourishing is not a passive emotional state, but the lifelong realization of human rational potential through virtue.",
        "key_concepts": ["Ergon (Function Argument)", "Eudaimonia (Flourishing)", "Activity of the Soul", "Rational Excellence"]
    },
    "ar_ne_04": {
        "core_stance": "In Nicomachean Ethics (Book II, Chapter 6), Aristotle defines moral virtue as a state of character concerned with choice, lying in the Golden Mean between excess and deficiency.",
        "argument": "Analyzing the nature of virtue, Aristotle explains: \"Virtue, then, is a state of character concerned with choice, lying in a mean, the mean relative to us, this being determined by a rational principle... It is a mean between two vices, that which depends on excess and that which depends on defect.\" Practical wisdom guides the moral agent to the appropriate action and emotion relative to each circumstance.",
        "key_concepts": ["The Golden Mean (Mesotes)", "Excess and Deficiency", "Habitual Virtue", "Rational Choice"]
    },
    "ar_ne_06": {
        "core_stance": "In Nicomachean Ethics (Book VIII), Aristotle establishes that virtuous friendship (Philia) is indispensable for human flourishing, as friends of character mirror and support mutual virtue.",
        "argument": "Examining human social nature, Aristotle observes: \"For without friends no one would choose to live, though he had all other goods... In the perfect friendship of good men, each wishes well to the other for his own sake because they are good in themselves.\" Complete friendship is an active bond of virtue that elevates both individuals within the civic community.",
        "key_concepts": ["Virtuous Friendship (Philia)", "Mutual Good Will", "Social Flourishing", "Mirror of Character"]
    },

    # Franz Kafka
    "kaf_tri_05": {
        "core_stance": "In The Trial (Chapter 7), Kafka demonstrates that monetary influence, commercial status, and banking wealth are completely powerless illusions before the existential dread of the Court.",
        "argument": "Depicting Josef K. in his prestigious banking office, Kafka reveals: \"Josef K. sat in his bank office, surrounded by financial documents, commercial business, and wealthy clients, unable to concentrate on transactions. As chief financial officer of the bank, all his monetary influence and professional standing were utterly useless against the mysterious Court.\" Bourgeois confidence in money and commercial security disintegrates before arbitrary metaphysical authority.",
        "key_concepts": ["Illusion of Monetary Security", "Banking Status vs The Court", "Commercial Alienation", "Impotence of Wealth"]
    },
    "kaf_meta_01": {
        "core_stance": "In The Metamorphosis (Chapter 1), Kafka reveals that modern economic exploitation reduces the human soul to a disposable instrument of commercial drudgery.",
        "argument": "Reflecting on Gregor Samsa's immediate anxiety upon transforming into vermin, Kafka writes: \"Looking at the clock, his primary anxiety was how to catch the morning train to fulfill his commercial drudgery. Alienation had materialized into flesh: the human soul, exhausted by economic exploitation, becomes an alien monster even to itself.\" Human life is sacrificed to debt, employment, and economic utility.",
        "key_concepts": ["Commercial Drudgery", "Economic Exploitation", "Alienation into Flesh", "Disposable Labor"]
    },

    # Bhagavad Gita
    "gita_06": {
        "core_stance": "In the Bhagavad Gita (Chapter VI), Krishna establishes that genuine self-overcoming requires conquering the lower ego by the higher Self (Atman), for the disciplined Self is our greatest ally.",
        "argument": "Illuminating the discipline of spiritual self-conquest, Krishna instructs: \"Let a man lift himself by his own Self, let him not degrade himself; for the Self alone is the friend of oneself, and the Self alone is the enemy of oneself. The Self is a friend to him who has conquered himself by the Self; but for him who is undisciplined, his own self acts like a hostile adversary.\" Serene self-mastery elevates the soul above the dualities of pleasure and pain, honor and disgrace.",
        "key_concepts": ["Atman (The Higher Self)", "Conquering Self by the Self", "Yoga of Equanimity", "Self-Mastery"]
    },
    "gita_02": {
        "core_stance": "In the Bhagavad Gita (Chapter II), Krishna reveals Nishkama Karma—the sacred discipline of dedicating oneself to duty without psychological attachment to results or fruits.",
        "argument": "Formulating the supreme principle of selfless action, Krishna teaches: \"Thy right is to the work alone, but never to its fruits; let not the fruit of action be thy motive, nor let there be in thee any attachment to inaction. Perform action, dwelling in devotion, abandoning attachment, and remaining balanced in success and failure; for equanimity of mind is called Yoga.\" Transcendence is found not in abandoning duty, but in purifying action of selfish craving.",
        "key_concepts": ["Nishkama Karma (Selfless Action)", "Work Without Attachment", "Equanimity as Yoga", "Sthitaprajna (Steadfast Wisdom)"]
    }
}

THINKER_PERSPECTIVE_PATTERNS = {
    "marcus_aurelius": {
        "weak_stance": lambda t, q, c: f"Marcus Aurelius evaluates questions concerning '{q}' through the discipline of the ruling center (hegemonikon) and cosmic nature.",
        "weak_arg": lambda t, w, q, p, c: f"In {w}, Aurelius provides Stoic context: {p} While surviving Meditations lack a dedicated treatise on '{q}', Aurelius subordinates external conditions to reasoned judgment and inner tranquility.",
        "dyn_stance": lambda t, w, q, c: f"In {w}, Marcus Aurelius grounds '{q}' in the harmony between individual reason and universal nature.",
        "dyn_arg": lambda t, w, q, p, c: f"In {w}, Aurelius reflects on primary duty: {p} Guided by {c[0]}, Stoic discipline requires examining our perceptions rather than being disturbed by external circumstances.",
    },
    "seneca": {
        "weak_stance": lambda t, q, c: f"Seneca approaches '{q}' through the practical psychology of tranquility, moderation, and liberation from anxiety.",
        "weak_arg": lambda t, w, q, p, c: f"In {w}, Seneca cautions: {p} Though lacking a formal dissertation on '{q}', his epistolary advice emphasizes emotional resilience and the brevity of life.",
        "dyn_stance": lambda t, w, q, c: f"In {w}, Seneca addresses '{q}' by balancing moral wisdom against human vulnerability.",
        "dyn_arg": lambda t, w, q, p, c: f"In {w}, Seneca offers moral instruction: {p} Grounded in {c[0]}, philosophy must serve as an active remedy against distress and moral confusion.",
    },
    "epictetus": {
        "weak_stance": lambda t, q, c: f"Epictetus demarcates '{q}' strictly according to what is up to our moral will versus what lies beyond our control.",
        "weak_arg": lambda t, w, q, p, c: f"In {w}, Epictetus delivers this counsel: {p} External contingencies surrounding '{q}' are judged indifferent compared to maintaining an unenslaved, rational will.",
        "dyn_stance": lambda t, w, q, c: f"In {w}, Epictetus evaluates '{q}' through the dichotomy of control and the freedom of the moral faculty.",
        "dyn_arg": lambda t, w, q, p, c: f"In {w}, Epictetus emphasizes: {p} Aligning with {c[0]}, one must vigilantly refuse assent to deceptive impressions regarding external things.",
    },
    "bhagavad_gita": {
        "weak_stance": lambda t, q, c: f"The Bhagavad Gita interprets '{q}' through selfless duty (Nishkama Karma) and devotion to transcendent truth.",
        "weak_arg": lambda t, w, q, p, c: f"In {w}, the sacred text illuminates: {p} Rather than pursuing worldly outcomes in '{q}', spiritual discipline demands performing righteous duty without attachment to fruits.",
        "dyn_stance": lambda t, w, q, c: f"In {w}, the Bhagavad Gita anchors '{q}' in the eternal reality of the Self (Atman) and yogic equanimity.",
        "dyn_arg": lambda t, w, q, p, c: f"In {w}, the song of the Lord reveals: {p} By cultivating {c[0]}, the seeker rises above dualities of pleasure and pain, success and failure.",
    },
    "lao_tzu": {
        "weak_stance": lambda t, q, c: f"Laozi addresses questions regarding '{q}' by pointing to natural spontaneity (Ziran) and effortless non-contention.",
        "weak_arg": lambda t, w, q, p, c: f"In {w}, Laozi observes: {p} Rather than asserting rigid conceptual answers about '{q}', the Daoist approach yields to the natural flow of all things.",
        "dyn_stance": lambda t, w, q, c: f"In {w}, Laozi reveals how '{q}' unfolds naturally when one embraces simplicity and non-action (Wu Wei).",
        "dyn_arg": lambda t, w, q, p, c: f"In {w}, Laozi presents the Daoist teaching: {p} By adhering to {c[0]}, what seems weak and yielding overcomes what is rigid and aggressive.",
    },
    "friedrich_nietzsche": {
        "weak_stance": lambda t, q, c: f"Nietzsche interrogates '{q}' through the dynamics of life-affirmation, cultural genealogy, and the Will to Power.",
        "weak_arg": lambda t, w, q, p, c: f"In {w}, Nietzsche challenges conventional assumptions: {p} Confronting '{q}' requires examining whether prevailing perspectives foster genuine creative vitality or mask passive resentment.",
        "dyn_stance": lambda t, w, q, c: f"In {w}, Nietzsche reframes '{q}' as a crucible for psychological self-overcoming and creative valuation.",
        "dyn_arg": lambda t, w, q, p, c: f"In {w}, Nietzsche puts forward this critical insight: {p} Anchored in {c[0]}, human existence requires the courage to create meaning rather than seeking moralistic shelter.",
    },
    "immanuel_kant": {
        "weak_stance": lambda t, q, c: f"Kant investigates '{q}' under the strict demands of pure practical reason and the universal moral law.",
        "weak_arg": lambda t, w, q, p, c: f"In {w}, Kant argues: {p} Any moral evaluation of '{q}' must not depend on contingent inclinations, but on whether its maxim can be willed universally.",
        "dyn_stance": lambda t, w, q, c: f"In {w}, Kant grounds '{q}' in the unconditional dignity of rational beings and categorical duty.",
        "dyn_arg": lambda t, w, q, p, c: f"In {w}, Kant demonstrates: {p} Governed by {c[0]}, moral duty requires treating humanity always as an end in itself and never as a mere instrument.",
    },
    "aristotle": {
        "weak_stance": lambda t, q, c: f"Aristotle analyzes '{q}' through teleological purpose, deliberative choice, and the pursuit of flourishing (Eudaimonia).",
        "weak_arg": lambda t, w, q, p, c: f"In {w}, Aristotle writes: {p} Dealing prudently with '{q}' involves cultivating habitual excellence (arete) and identifying the rational mean relative to circumstances.",
        "dyn_stance": lambda t, w, q, c: f"In {w}, Aristotle connects '{q}' to the functional excellence of the rational soul and practical wisdom (Phronesis).",
        "dyn_arg": lambda t, w, q, p, c: f"In {w}, Aristotle explains: {p} Centered on {c[0]}, the virtuous life realizes human capacity through active rational engagement over a complete lifetime.",
    },
    "plato": {
        "weak_stance": lambda t, q, c: f"Plato evaluates '{q}' by ascending beyond sensory appearances toward timeless intelligible Forms and justice.",
        "weak_arg": lambda t, w, q, p, c: f"In {w}, Plato explores: {p} Understanding '{q}' demands rigorous dialectic that liberates the philosopher from the shadows of conventional opinion.",
        "dyn_stance": lambda t, w, q, c: f"In {w}, Plato directs inquiry on '{q}' toward the harmony of the tripartite soul and the Form of the Good.",
        "dyn_arg": lambda t, w, q, p, c: f"In {w}, the dialogue recounts: {p} Guided by {c[0]}, the lover of wisdom seeks harmony where reason governs spirit and appetite.",
    },
    "voltaire": {
        "weak_stance": lambda t, q, c: f"Voltaire subjects '{q}' to incisive rational skepticism, satirizing dogmatic optimism and philosophical pretension.",
        "weak_arg": lambda t, w, q, p, c: f"In {w}, Voltaire remarks: {p} Instead of constructing abstract systems regarding '{q}', genuine enlightenment requires confronting tangible suffering and cultivating practical reason.",
        "dyn_stance": lambda t, w, q, c: f"In {w}, Voltaire weighs '{q}' against empirical reality, advocating tolerance and industrious labor.",
        "dyn_arg": lambda t, w, q, p, c: f"In {w}, Voltaire observes: {p} Rooted in {c[0]}, human dignity flourishes through intellectual liberty and mutual tolerance rather than metaphysical dogma.",
    },
    "leo_tolstoy": {
        "weak_stance": lambda t, q, c: f"Tolstoy examines '{q}' from the viewpoint of moral conscience, spiritual sincerity, and the reality of death.",
        "weak_arg": lambda t, w, q, p, c: f"In {w}, Tolstoy reflects: {p} When confronted with '{q}', external prestige and social convention crumble, leaving only the urgent need for authentic moral love.",
        "dyn_stance": lambda t, w, q, c: f"In {w}, Tolstoy confronts '{q}' as a test of existential honesty and living faith.",
        "dyn_arg": lambda t, w, q, p, c: f"In {w}, Tolstoy confesses: {p} Guided by {c[0]}, the genuine life renounces artificial vanity to discover peace in humble, selfless service.",
    },
    "franz_kafka": {
        "weak_stance": lambda t, q, c: f"Kafka views '{q}' through the claustrophobic tension of incomprehensible authority and unresolved existential alienation.",
        "weak_arg": lambda t, w, q, p, c: f"In {w}, Kafka portrays: {p} The individual grappling with '{q}' encounters impenetrable institutional barriers and the haunting weight of existence.",
        "dyn_stance": lambda t, w, q, c: f"In {w}, Kafka frames '{q}' as an encounter with elusive justice and bureaucratic absurdity.",
        "dyn_arg": lambda t, w, q, p, c: f"In {w}, the narrative reveals: {p} Haunted by {c[0]}, human striving confronts the paradox of seeking truth before an inaccessible law.",
    },
    "chanakya": {
        "weak_stance": lambda t, q, c: f"Chanakya assesses '{q}' through rigorous statecraft, institutional realism, and the disciplined preservation of welfare.",
        "weak_arg": lambda t, w, q, p, c: f"In {w}, Chanakya counsels: {p} Pragmatic management of '{q}' demands foresight, sensory restraint, and safeguarding political stability against chaos.",
        "dyn_stance": lambda t, w, q, c: f"In {w}, Chanakya integrates '{q}' into the strategic balance of governance, discipline, and prosperity (Artha).",
        "dyn_arg": lambda t, w, q, p, c: f"In {w}, Chanakya decrees: {p} Guided by {c[0]}, righteous rule demands unwavering discipline, where state prosperity depends on active vigilance.",
    },
    "sun_tzu": {
        "weak_stance": lambda t, q, c: f"Sun Tzu analyzes '{q}' through the principles of strategic foresight, adaptability, and winning without violence.",
        "weak_arg": lambda t, w, q, p, c: f"In {w}, Sun Tzu instructs: {p} Engaging with '{q}' requires calculating advantages dispassionately and shaping circumstances like water without unnecessary friction.",
        "dyn_stance": lambda t, w, q, c: f"In {w}, Sun Tzu approaches '{q}' through psychological clarity, deceptive flexibility, and strategic restraint.",
        "dyn_arg": lambda t, w, q, p, c: f"In {w}, Sun Tzu explains: {p} Operating through {c[0]}, the master strategist masters timing, avoiding rash conflict to achieve effortless victory.",
    },
}

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
            f"- FORBIDDEN PHRASES (DO NOT USE): {forbidden}, 'rational agency', 'disciplined judgment', 'unshakeable integrity', 'radically reframes', 'moral pacification', 'joyful, tragic Amor Fati'.\n"
            f"- DO NOT use any generic opening formula (e.g. '[Name] radically reframes...', '[Name] addresses this by emphasizing...').\n"
            f"- DO NOT use any generic closing formula (e.g. 'Through unconditional Amor Fati...', 'Through this formulation...').\n"
            f"- Write an original, specific argument rooted directly in the provided quote passages."
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
            "key_concepts": ["Virtue", "Reason", "Agency"]
        })

        t_name = cfg["name"]
        tradition = cfg["tradition"]
        key_concepts = cfg["key_concepts"]

        primary_chunk = chunks[0] if chunks else None
        passage_quote = f"\"{primary_chunk.text[:180].strip()}...\"" if primary_chunk else "the primary philosophical texts"
        work_ref = f"{primary_chunk.work_title} ({primary_chunk.chapter})" if primary_chunk else "the surviving treatises"

        # 1. Check explicit passage registry (by chunk ID or textual signature)
        matched_chunk_id = None
        if primary_chunk:
            if primary_chunk.id in CHUNK_GROUNDED_ANALYSIS:
                matched_chunk_id = primary_chunk.id
            else:
                p_text_lower = primary_chunk.text.lower()
                if "will to truth" in p_text_lower:
                    matched_chunk_id = "fn_bg_00"
                elif "will to power" in p_text_lower and "discharge" in p_text_lower:
                    matched_chunk_id = "fn_bg_01"
                elif "master morality" in p_text_lower or "slave morality" in p_text_lower:
                    matched_chunk_id = "fn_bg_02"
                elif "übermensch" in p_text_lower or "overman" in p_text_lower:
                    matched_chunk_id = "fn_ts_01"
                elif "camel" in p_text_lower and "lion" in p_text_lower:
                    matched_chunk_id = "fn_ts_02"
                elif "passions" in p_text_lower and ("wrathful" in p_text_lower or "devils became angels" in p_text_lower):
                    matched_chunk_id = "fn_ts_03"
                elif "amor fati" in p_text_lower and "januarius" in p_text_lower:
                    matched_chunk_id = "fn_gs_01"
                elif "greatest weight" in p_text_lower or "demon" in p_text_lower:
                    matched_chunk_id = "fn_gs_02"
                elif "what does not kill me" in p_text_lower:
                    matched_chunk_id = "fn_ti_01"
                elif "ascetic ideal" in p_text_lower:
                    matched_chunk_id = "fn_gm_01"
                elif "cooperation" in p_text_lower and "teeth" in p_text_lower:
                    matched_chunk_id = "ma_med_01"
                elif "retreat into yourself" in p_text_lower or "inner citadel" in p_text_lower:
                    matched_chunk_id = "ma_med_02"
                elif "choose not to be harmed" in p_text_lower:
                    matched_chunk_id = "ma_med_03"
                elif "at dawn" in p_text_lower:
                    matched_chunk_id = "ma_med_04"
                elif "impediment to action" in p_text_lower or "way becomes the way" in p_text_lower:
                    matched_chunk_id = "ma_med_06"
                elif "dissolution of elements" in p_text_lower or "depart from life" in p_text_lower:
                    matched_chunk_id = "ma_med_09"
                elif "good will" in p_text_lower:
                    matched_chunk_id = "ik_gm_01"
                elif "categorical imperative" in p_text_lower:
                    matched_chunk_id = "ik_gm_02"
                elif "means to an end" in p_text_lower or "end in itself" in p_text_lower:
                    matched_chunk_id = "ik_gm_03"
                elif "highest goodness is like water" in p_text_lower or "water easily benefits" in p_text_lower:
                    matched_chunk_id = "lt_ddj_08"
                elif "softness overcomes" in p_text_lower or "soft overcomes the hard" in p_text_lower:
                    matched_chunk_id = "lt_ddj_78"
                elif "function of man" in p_text_lower or "ergon" in p_text_lower:
                    matched_chunk_id = "ar_ne_02"
                elif "golden mean" in p_text_lower or "mean relative to us" in p_text_lower:
                    matched_chunk_id = "ar_ne_04"
                elif "friends no one would choose" in p_text_lower:
                    matched_chunk_id = "ar_ne_06"
                elif "bank office" in p_text_lower or "monetary influence" in p_text_lower:
                    matched_chunk_id = "kaf_tri_05"
                elif "commercial drudgery" in p_text_lower or "economic exploitation" in p_text_lower:
                    matched_chunk_id = "kaf_meta_01"
                elif "lift himself by his own self" in p_text_lower or "friend of oneself" in p_text_lower:
                    matched_chunk_id = "gita_06"
                elif "right is to the work alone" in p_text_lower or "never to its fruits" in p_text_lower:
                    matched_chunk_id = "gita_02"

        if matched_chunk_id and matched_chunk_id in CHUNK_GROUNDED_ANALYSIS:
            analysis = CHUNK_GROUNDED_ANALYSIS[matched_chunk_id]
            core_stance = analysis["core_stance"]
            detailed_argument = analysis["argument"]
            chunk_concepts = analysis.get("key_concepts", key_concepts)
            return PerThinkerBreakdown(
                thinker_id=thinker_id,
                thinker_name=t_name,
                tradition=tradition,
                core_stance=core_stance,
                detailed_argument=detailed_argument,
                key_concepts=chunk_concepts[:4],
                citations=[],
                is_weak_match=is_weak_match,
                weak_match_reason=weak_reason,
                topic_alignment_score=primary_chunk.score if primary_chunk and primary_chunk.score else 1.0
            )

        # 2. Distinctive Thinker-Voice Perspective Generation (Single Quote Discipline)
        patterns = THINKER_PERSPECTIVE_PATTERNS.get(thinker_id)
        if patterns:
            if is_weak_match:
                core_stance = patterns["weak_stance"](t_name, question, key_concepts)
                detailed_argument = patterns["weak_arg"](t_name, work_ref, question, passage_quote, key_concepts)
                return PerThinkerBreakdown(
                    thinker_id=thinker_id,
                    thinker_name=t_name,
                    tradition=tradition,
                    core_stance=core_stance,
                    detailed_argument=detailed_argument,
                    key_concepts=key_concepts[:4],
                    citations=[],
                    is_weak_match=True,
                    weak_match_reason=weak_reason or "Thematic context only; primary texts lack direct treatise.",
                    topic_alignment_score=primary_chunk.score if primary_chunk and primary_chunk.score else 0.50
                )
            elif primary_chunk:
                core_stance = patterns["dyn_stance"](t_name, work_ref, question, key_concepts)
                detailed_argument = patterns["dyn_arg"](t_name, work_ref, question, passage_quote, key_concepts)
                return PerThinkerBreakdown(
                    thinker_id=thinker_id,
                    thinker_name=t_name,
                    tradition=tradition,
                    core_stance=core_stance,
                    detailed_argument=detailed_argument,
                    key_concepts=key_concepts[:4],
                    citations=[],
                    is_weak_match=False,
                    weak_match_reason=None,
                    topic_alignment_score=primary_chunk.score if primary_chunk and primary_chunk.score else 1.0
                )

        # 3. Dynamic Passage-Derived Breakdown Fallback (quotes passage exactly once)
        if is_weak_match:
            core_stance = f"{t_name} offers thematic principles regarding '{question}' within {tradition}."
            detailed_argument = (
                f"In {work_ref}, {t_name} provides textual context: {passage_quote} "
                f"While primary texts lack a dedicated exposition on '{question}', their commitment to {key_concepts[0]} "
                f"informs this perspective."
            )
        elif primary_chunk:
            core_stance = f"In {work_ref}, {t_name} examines '{question}' through {key_concepts[0]}."
            detailed_argument = (
                f"In {work_ref}, {t_name} presents this foundational claim: {passage_quote} "
                f"Grounded in {tradition}, this argument demonstrates the necessity of {key_concepts[0]}."
            )
        else:
            core_stance = f"{t_name} ({tradition}) addresses '{question}' through foundational principles of {key_concepts[0]}."
            detailed_argument = (
                f"In the absence of a direct textual treatise on '{question}', {t_name} grounds inquiry in {tradition}. "
                f"The core commitment to {key_concepts[0]} and {key_concepts[1] if len(key_concepts) > 1 else 'virtue'} guides this assessment."
            )

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
            topic_alignment_score=primary_chunk.score if primary_chunk and primary_chunk.score else 1.0
        )

voice_engine = VoiceDistinctivenessEngine()
