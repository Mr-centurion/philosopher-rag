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
        "anger", "wrath", "rage", "resentment", "ressentiment", "hatred", "bitterness", "irritation", "fury"
    ],
    "thinking": [
        "thinking", "thought", "thoughts", "reason", "rational", "rationality", "clarity",
        "clearly", "mind", "intellect", "judgment", "governing mind", "ruling center",
        "hegemonikon", "practical wisdom", "phronesis", "understanding", "logos",
        "objective judgment", "clear", "discernment", "deliberation"
    ],
    "god": [
        "god", "divine", "logos", "heavens", "cosmos", "providence", "nature", "dao", "tao"
    ],
    "money": [
        "money", "wealth", "riches", "poverty", "poor", "property", "possessions",
        "financial", "finance", "commercial", "gold", "silver", "coins", "greed",
        "avarice", "economic", "commerce", "business", "profit", "gain", "loss of wealth",
        "luxury", "fortune", "bank", "ledger", "monetary", "capital", "currency"
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
        "morality": ["good and evil", "wrongdoer", "share of the divine", "nature demands", "objective judgment", "unselfish action", "human life"],
        "anger": ["nor can i feel angry", "nature related to my own", "made for cooperation", "anger is unmanly", "passion", "ruling center", "governing mind", "no reason to torment yourself"],
        "thinking": ["governing mind", "ruling center", "objective judgment", "wipe out impressions", "think clearly", "reason", "logos", "serene mind", "ruling reason"]
    },
    "seneca": {
        "death": ["despising death", "fear death", "die honourably", "mortal", "fastidious man may wish to die", "death takes them away", "no pain before our birth", "cycle", "facing the end", "memento mori", "perish"],
        "suffering": ["pain is slight", "opinion has added nothing", "torment is brought to an end", "rouse yourself to resist", "according to opinion that we suffer", "wretched", "bear it is a noble deed", "pang", "grief", "endure", "bear pain"],
        "friendship": ["loss of a friend", "dry eyes", "recover your friend by tears", "memory of dead friends", "quiet pleasure", "self-sufficient", "bear the loss with equanimity", "art of making friends", "rescue from the enemy", "worthy of friendship", "comrades"],
        "society": ["they are slaves", "fellow-slaves", "comrades", "humble friends", "fortune has equal power", "same stock", "breathes lives and dies", "treat your inferior", "slave to fear ambition or desire", "fellow man"],
        "anxiety": ["flee along with yourself", "burdens of the mind", "globetrotting", "change your soul not your climate", "travel with your ailments", "restlessness in vain", "fear", "dread"],
        "harm": ["opinion has added nothing", "according to opinion that we suffer", "wretched", "strip off the mask", "bare reality", "fortune"],
        "duty": ["hold every hour", "lay hold of to-day's task", "time speeds by", "ownership of time", "single fleeting possession", "precious commodity", "die honourably"],
        "thinking": ["change your soul not your climate", "strip off the mask", "bare reality", "opinion", "equanimity", "philosophy"]
    },
    "epictetus": {
        "harm": ["no one will hurt you", "will not be harmed", "opinion alone which has provoked you", "principles and notions", "not he who gives ill language insults", "slavish"],
        "insult": ["not he who gives ill language or a blow insults", "principle which represents these things as insulting", "opinion alone which has provoked you", "abuse or mockery", "pity him rather than burn with resentment", "delay", "master of yourself", "provocation"],
        "suffering": ["men are disturbed not by things", "notions which they form concerning things", "hindered or disturbed or grieved", "sickness is a hindrance to the body", "lameness", "wish them to happen as they do happen"],
        "death": ["death is not terrible", "terror consists in our notion of death", "socrates", "wife and children should live for ever", "actor in a drama", "wish them to happen as they do happen"],
        "desire": ["dichotomy of control", "in our control", "not in our control", "he is free who lives as he likes", "seek not that which is impossible", "disappointed in your desires"],
        "duty": ["actor in a drama", "act well the character assigned you", "prescribe some character", "inward moral conviction", "be silent", "dignity"],
        "anger": ["opinion alone which has provoked you", "pity him rather than burn with resentment", "gain time and delay", "not hurried away by appearance", "master of yourself"],
        "thinking": ["principles and opinions", "prohairesis", "dichotomy of control", "not hurried away by appearance", "gain time and delay", "inward moral conviction", "judgments"]
    },
    "plato": {
        "leadership": ["philosopher-king", "kings and princes", "political greatness and wisdom meet in one", "cities will never have rest", "govern", "ruler", "guardians"],
        "thinking": ["allegory of the cave", "shadows of the images", "sun itself", "contemplate the good", "unexamined life is not worth living", "dialectic", "forms", "opinion", "knowledge", "reason"],
        "morality": ["justice", "ring of gyges", "injustice", "virtue is not given by money", "care for the soul", "improvement of the soul", "tripartite soul", "good man"],
        "virtue": ["virtue is not given by money", "improvement of the soul", "care for wisdom and truth", "daily converse about virtue", "unexamined life", "justice", "temperance", "noble"],
        "death": ["death is a good", "migration of the soul", "sleep undisturbed by dreams", "no evil can happen to a good man", "fortunes not neglected by gods", "facing death"],
        "harm": ["no evil can happen to a good man", "unjust man enslaved by tyrannical desires", "most wretched", "cannot be harmed"],
        "society": ["philosopher-king", "justice in the state", "cities will never have rest from evils", "men of athens", "public as well as private", "community"],
        "desire": ["appetitive element", "craves bodily pleasures", "ring of gyges", "invisible", "tyrannical desires", "temperance"]
    },
    "voltaire": {
        "suffering": ["cultivate our garden", "diminish human misery", "physical and moral evil", "sorrow and disease", "mockery of human suffering", "sterile lamentation", "kindness"],
        "morality": ["tolerance", "first law of nature", "appurtenance of humanity", "pardon each other our follies", "justice is the bond of society", "fanaticism", "mutual equity"],
        "society": ["tolerance is its only remedy", "discord is the great evil", "pardon our follies", "holy wars", "justice is the bond of society", "hawks and pigeons", "civilization", "brother"],
        "harm": ["persecutes a man his brother", "infectious malady", "spiritual rabies", "discord", "human cruelty", "fanaticism", "massacred each other"],
        "thinking": ["cultivate our garden", "pangloss", "best of all possible worlds", "philosophical spirit", "reason alone can cure contagion", "dogma", "metaphysical systems"],
        "god": ["origin of evil", "benevolence", "omnipotence", "superstition", "fanaticism", "holy wars", "theological"]
    },
    "leo_tolstoy": {
        "suffering": ["crisis of meaning", "dragon of death", "drops of honey", "standstill", "precipice", "existential nihilism", "torment", "falsity", "despair"],
        "death": ["death of ivan ilyich", "dragon of death", "where is death", "in place of death light", "fear of death vanished", "dying", "precipice", "facing death"],
        "god": ["to know god is to live", "god is life", "faith", "faith connects finite with infinite", "surrender to god", "infinite compassion"],
        "morality": ["selfless labor", "love of neighbor", "faith of simple people", "peasants", "humility", "artificial falsehood", "moral duty"],
        "thinking": ["crisis of meaning", "why should i live", "rational knowledge leads to despair", "faith alone gives meaning", "falsehood of conventional life"],
        "society": ["conventional life", "bourgeois", "deception and the lie", "simple working people", "peasants", "love your neighbor"]
    },
    "franz_kafka": {
        "suffering": ["before the law", "the trial", "arrested without cause", "like a dog", "monstrous vermin", "rotting apple", "alienation", "helplessly", "absurd"],
        "harm": ["arrested without cause", "court attracted by guilt", "like a dog", "shame outlive him", "intolerable parasite", "cast out", "rotting apple"],
        "society": ["nameless authority", "incomprehensible apparatus", "economic utility", "commercial drudgery", "intolerable parasite", "modern existence", "bureaucratic"],
        "morality": ["innocence is no defense", "guilt", "before the law", "doorkeeper", "shame", "unspoken verdict", "secret power", "justice"],
        "death": ["like a dog", "final horror", "quiet darkness before dawn", "breathed his last sigh", "disappear", "knife into heart"],
        "thinking": ["before the law", "parable", "court", "absurd", "alienation", "existential", "labyrinth", "doorkeeper", "incomprehensible"],
        "loneliness": ["alienation materialized into flesh", "monster even to itself", "words no longer understood", "severing of human bonds", "solitude", "isolation"],
        "money": ["bank", "financial documents", "commercial business", "monetary influence", "economic utility", "commercial drudgery", "economic exploitation", "wealth", "bourgeois", "ledger balances"]
    },
    "bhagavad_gita": {
        "duty": ["nishkama karma", "action without attachment", "right is to the work alone", "never to its fruits", "svadharma", "allotted duty", "karma yoga", "action superior to inaction"],
        "action": ["nishkama karma", "right is to the work", "fruits of action", "equanimity is yoga", "action in inaction", "devotion", "abandoning attachment"],
        "suffering": ["not shaken amidst afflictions", "equanimity in success and failure", "pleasure and pain", "honor and dishonor", "cold and heat", "craving fled away"],
        "death": ["immortality of soul", "atman", "never the spirit was born", "weapons cleave it not", "worn-out garments", "birthless deathless changeless", "facing death"],
        "thinking": ["sthitaprajna", "settled wisdom", "steadfast mind", "tortoise draws in its limbs", "jnana yoga", "fire of wisdom", "self alone is friend"],
        "harm": ["weapons cleave it not", "fire burneth it not", "untouched by sin", "lotus leaf", "self friend and enemy", "unwavering"],
        "god": ["surrendering actions unto supreme", "krishna", "eternal", "moksha", "liberation", "lokasangraha", "sacrifice", "devotion"]
    },
    "chanakya": {
        "leadership": ["happiness of subjects", "welfare of subjects", "king", "ruler", "indriyajaya", "restraint of senses", "energetic", "mandala", "sovereign", "alliances"],
        "power": ["rod of justice", "danda", "strength is cause of peace", "alliances and treaties", "law of the fish", "matsya-nyaya", "crush an irreconcilable foe"],
        "society": ["happiness of subjects", "welfare of subjects", "circle of states", "mandala", "alliances", "law of the fish", "security of life", "subjects"],
        "friendship": ["test a friend in adversity", "disaster famine war", "cremation ground", "unconditional trust", "weaponize vulnerabilities", "no companion"],
        "harm": ["law of the fish", "matsya-nyaya", "weaponize vulnerabilities", "approaching danger from afar", "protect wealth", "protect life"],
        "thinking": ["strategic prudence", "indriyajaya", "realist discernment", "extract nectar from poison", "straight trees felled first", "foresight", "vigilant intellect"],
        "anger": ["six internal enemies", "lust anger greed vanity", "arbitrary wrath", "incites revolt", "friend become angry"]
    },
    "sun_tzu": {
        "aggression": ["art of war", "victory without fighting", "balk the enemy plans", "attack by stratagem", "tactics like water", "invincibility", "conflict", "strategic"],
        "leadership": ["highest generalship", "know enemy and know yourself", "when to fight and when not to fight", "enlightened ruler is heedful", "general full of caution"],
        "thinking": ["know enemy and yourself", "ponder and deliberate", "tactics like water", "no constant shape", "deception", "artifice of deviation", "foreknowledge"],
        "anger": ["gratify anger", "fight out of pique", "anger may change to gladness", "vexation", "caution", "heedful"],
        "action": ["rapidity of wind", "compactness of forest", "like fire", "immovability like mountain", "fall like thunderbolt", "modify tactics", "water"],
        "harm": ["invincibility lies in defence", "kingdom destroyed cannot come again", "dead cannot be brought back", "safety or ruin"]
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
        "happiness": ["school of war", "why in life", "man does not strive after happiness", "will to power", "discharge strength"],
        "anger": ["ressentiment", "contempt", "will to power", "school of war", "overcoming", "passions", "sublimation"],
        "thinking": ["free spirit", "intellectual integrity", "great reason of the body", "sublimation", "perspective", "values"]
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
        "harm": ["good will", "autonomy", "heteronomy", "moral law", "courage", "resolution"],
        "anger": ["passion", "moral law", "duty", "practical reason", "categorical imperative", "autonomy"],
        "thinking": ["pure reason", "practical reason", "sapere aude", "enlightenment", "think for oneself", "understanding", "judgment", "maxims"]
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
        "morality": ["virtue", "arete", "doctrine of the mean", "phronesis", "aim at some good", "chief good", "just acts", "political animal"],
        "anger": ["doctrine of the mean", "good temper", "mean with respect to anger", "proper degree", "courage", "passion", "justifiable indignation"],
        "thinking": ["phronesis", "practical wisdom", "deliberation", "intellectual virtue", "rational soul", "logos", "right reason"]
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
        "morality": ["supreme good like water", "benevolent", "trustworthy", "dao", "wu wei", "goodness as good", "not self-righteous"],
        "anger": ["does not contend", "softness overcomes hardness", "water", "without anger", "stillness", "harmony", "peace"],
        "thinking": ["stillness", "emptiness", "clarity", "simplicity", "without desire", "know oneself", "enlightenment", "natural course"]
    }
}

STOPWORDS = {
    "what", "does", "say", "about", "how", "why", "who", "when", "where", "is", "are",
    "the", "a", "an", "and", "or", "in", "on", "to", "for", "with", "by", "from",
    "aurelius", "nietzsche", "kant", "aristotle", "laozi", "lao", "tzu", "marcus",
    "friedrich", "immanuel", "think", "explain", "view", "views", "teach", "tell", "me",
    "taking", "regarding", "between", "human", "life", "relation", "constitutes",
    "conflict", "personal", "universal", "achieved", "through", "active", "effortless",
    "facing", "would", "they", "being", "should", "one", "their", "respond", "react",
    "advice", "coping", "deal", "getting", "gets", "got",
    "franz", "kafka", "seneca", "epictetus", "plato", "voltaire", "tolstoy", "leo",
    "chanakya", "sun", "gita", "bhagavad", "arjuna", "krishna", "socrates",
    "perspectives", "perspective", "philosophers", "philosophy", "philosophical"
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
