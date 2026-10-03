# AI-ASSISTED: Cursor
# PROMPT: RAYA-only Tamil/Thanglish phrases (no jarvis triggers)
# ACCEPTED-BY: vignesh

from __future__ import annotations

import re

# Tamil script → English command tokens (longest phrases first at apply time)
_TAMIL_PHRASES: tuple[tuple[str, str], ...] = (
    ("சமீபத்திய test plan முடிவுகள்", "latest test plan results"),
    ("சமீப test plan முடிவுகள்", "latest test plan results"),
    ("சமீபத்திய முடிவுகள்", "show latest results"),
    ("சமீப முடிவு", "show latest result"),
    ("qe engine நிலை", "qe engine status"),
    ("workflow360 நிலை", "workflow360 status"),
    ("vanakkam raya", "hello raya"),
    ("வணக்கம் raya", "hello raya"),
    ("வணக்கம்", "hello raya"),
    ("நேரம் என்ன", "what time is it"),
    ("இன்றைய தேதி", "what is the date"),
    ("கணினி நிலை", "system status"),
    ("chrome திற", "open chrome"),
    ("browser திற", "open browser"),
    ("project analyze pannu", "analyze raya project"),
    ("raya project analyze", "analyze raya project"),
)

_TAMIL_WORDS: dict[str, str] = {
    "உதவி": "help",
    "கட்டளைகள்": "list commands",
    "காட்டு": "show",
    "சமீபத்திய": "latest",
    "சமீப": "latest",
    "முடிவுகள்": "results",
    "முடிவு": "result",
    "நிலை": "status",
    "நேரம்": "time",
    "தேதி": "date",
    "திற": "open",
    "நிறுத்து": "stop",
}

# Thanglish (Latin) phrase patterns → English triggers
_THANGLISH_PHRASES: tuple[tuple[str, str], ...] = (
    (r"\blatest\s+test\s+plan\s+result(?:s)?\s+(?:kaatu|kattu|show)\b", "latest test plan results"),
    (r"\btest\s+plan\s+result(?:s)?\s+(?:latest|recent|last)\b", "latest test plan results"),
    (r"\b(?:latest|recent|last)\s+result(?:s)?\s+(?:kaatu|kattu|thaa|kudu)\b", "show latest results"),
    (r"\bresult(?:s)?\s+(?:kaatu|kattu|thaa|kudu)\b", "show latest results"),
    (r"\bqe\s+engine\s+status\s+(?:paaru|paru|check)\b", "qe engine status"),
    (r"\bworkflow360\s+status\s+(?:paaru|paru)\b", "workflow360 status"),
    (r"\b(?:qe|workflow)\s+status\s+(?:paaru|paru|enna)\b", "qe engine status"),
    (r"\bchrome\s+(?:open|open\s+pannu|thir)\b", "open chrome"),
    (r"\bbrowser\s+(?:open|open\s+pannu|thir)\b", "open browser"),
    (r"\btime\s+enna\b", "what time is it"),
    (r"\beppo\s+time\b", "what time is it"),
    (r"\bdate\s+enna\b", "what is the date"),
    (r"\bhelp\s+venum\b", "help"),
    (r"\budhavi\s+venum\b", "help"),
    (r"\buthavi\s+venum\b", "help"),
    (r"\bvanakkam\b", "hello raya"),
    (r"\bvanakam\b", "hello raya"),
    (r"\bnanri\b", "thanks"),
    (r"\bregression\s+(?:run|pannu)\b", "run qe regression"),
    (r"\bconnected\s+project(?:s)?\s+(?:list|kaatu)\b", "list connected projects"),
    (r"\bcode\s+analyze\s+pannu\b", "analyze the codebase"),
    (r"\btpx[-\s]?\d+\s+result", "show execution result"),
)

_THANGLISH_FILLERS = frozenset(
    {
        "pannu",
        "panu",
        "venum",
        "venam",
        "da",
        "di",
        "la",
        "aa",
        "ah",
        "nu",
        "na",
        "ok",
        "pls",
        "please",
    },
)


def expand_tamil_and_thanglish(text: str) -> str:
    """Map Tamil script and common Thanglish to English trigger phrases."""
    if not text.strip():
        return text

    out = text
    for ta, en in _TAMIL_PHRASES:
        if ta in out:
            out = out.replace(ta, en)

    for ta, en in sorted(_TAMIL_WORDS.items(), key=lambda x: -len(x[0])):
        out = out.replace(ta, f" {en} ")

    lower = out.lower()
    for pattern, repl in _THANGLISH_PHRASES:
        lower = re.sub(pattern, repl, lower, flags=re.IGNORECASE)

    tokens = []
    for tok in lower.split():
        if tok in _THANGLISH_FILLERS:
            continue
        tokens.append(tok)
    return re.sub(r"\s+", " ", " ".join(tokens)).strip() or lower.strip()
