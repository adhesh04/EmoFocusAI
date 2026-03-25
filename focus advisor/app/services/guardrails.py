# guardrails.py
#
# WHAT IS A GUARDRAIL SYSTEM?
# Guardrails are checks that run BEFORE and AFTER the LLM to ensure:
# 1. The user's question is appropriate and on-topic
# 2. The LLM's answer doesn't contain harmful advice
# 3. The chatbot stays focused on its purpose (focus science)
#
# WHY THIS MATTERS FOR RECRUITERS:
# Any production AI system needs guardrails. This demonstrates you understand
# responsible AI deployment — a key skill for AI engineering roles.
#
# OUR THREE LAYERS:
# Layer 1 — Input check: Is the question safe and on-topic?
# Layer 2 — Output check: Is the LLM's answer safe?
# Layer 3 — Topic enforcement: Soft redirect for off-topic but harmless questions

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class GuardrailResult:
    """
    Result from a guardrail check.
    
    allowed: True = proceed normally, False = block and return the message
    message: The response to send the user if blocked (None = proceed)
    warning: Optional soft warning to append to a valid response
    category: What kind of issue was detected (for logging)
    """
    allowed: bool
    message: Optional[str] = None
    warning: Optional[str] = None
    category: Optional[str] = None


# ── Layer 1: Blocked topics (hard blocks — never answer these) ─────────────────
# These are questions we flat-out refuse, with a clear explanation why.
# The explanation is important — we don't just say "I can't help",
# we tell the user WHY and what they should do instead.

HARD_BLOCKED_PATTERNS = [
    {
        "patterns": [
            r"\b(adderall|ritalin|modafinil|vyvanse|concerta|amphetamine|methylphenidate)\b",
            r"\b(nootropic.*(buy|dose|stack|get|order))\b",
            r"\b(smart drug|cognitive enhancer.*(buy|dose|get))\b",
        ],
        "category": "prescription_drugs",
        "response": (
            "I can't provide advice on prescription stimulants or controlled substances — "
            "self-medicating with them is both dangerous and illegal without a prescription.\n\n"
            "That said, if focus is a real struggle for you, here's what the research actually supports:\n\n"
            "- **Sleep** is the single highest-leverage intervention — even one night of poor sleep "
            "degrades attention as much as being legally drunk.\n"
            "- **20-minute aerobic exercise** before study sessions increases BDNF and can improve "
            "focus for up to 2 hours afterward — comparable to low doses of stimulant medication.\n"
            "- **Structured work intervals** (50 min work / 10 min break) prevent cognitive fatigue buildup.\n\n"
            "If you genuinely suspect ADHD, please speak to a psychiatrist — proper diagnosis and "
            "treatment makes a real difference, and it starts with a professional, not self-medication."
        )
    },
    {
        "patterns": [
            r"\b(cocaine|crack|meth|crystal|mdma|lsd|mushroom.*(focus|study|cognitive))\b",
            r"\b(drug.*(study|focus|concentration|brain|cognitive))\b",
            r"\b(microdosing.*(study|work|focus|productivity))\b",
        ],
        "category": "illegal_drugs",
        "response": (
            "I can't recommend illegal substances — beyond being illegal, they carry serious "
            "health risks and the research on long-term cognitive effects is not encouraging.\n\n"
            "What actually works sustainably for focus:\n\n"
            "- **Caffeine + L-theanine** (found naturally in green tea) is one of the most "
            "well-researched legal cognitive combinations — alertness without jitteriness.\n"
            "- **Deep work blocks** with phone in another room — Gloria Mark's research shows "
            "it takes 23 minutes to fully recover from a single phone check.\n"
            "- **Cold water on your face** activates the dive reflex and immediately sharpens alertness.\n\n"
            "Want me to go deeper on any of these evidence-based approaches?"
        )
    },
    {
        "patterns": [
            r"\b(rob|steal|theft|shoplift|burglary)\b",
            r"\b(rob.*bank|steal.*money|break.*in)\b",
        ],
        "category": "illegal_activity",
        "response": (
            "That's not something I can help with — and I'd genuinely encourage you to step back "
            "from that line of thinking. Crimes like robbery carry severe consequences that affect "
            "your entire future.\n\n"
            "If there's something deeper going on — financial stress, feeling stuck, "
            "or just frustration — that's worth talking to someone about.\n\n"
            "What I *can* help with is cognitive performance and focus. If you're a student "
            "or professional under pressure, there are real evidence-based strategies that help. "
            "What's actually going on with your studies or work right now?"
        )
    },
    {
        "patterns": [
            r"\b(kill|shoot|stab|hurt|attack|harm)\b.*\b(professor|teacher|boss|colleague|classmate|someone)\b",
            r"\b(want to (kill|hurt|shoot|attack))\b",
            r"\b(murder|assault|violence against)\b",
        ],
        "category": "violence",
        "response": (
            "I can't help with anything involving harm to others — and I'm genuinely concerned "
            "if you're having those kinds of thoughts, even as frustration.\n\n"
            "If you're feeling overwhelmed, angry, or at a breaking point — that's real and it matters. "
            "Please talk to someone: a counsellor, a trusted friend, or a crisis line "
            "(iCall India: 9152987821 | International: text HOME to 741741).\n\n"
            "If this was frustration venting and you're actually struggling with focus, "
            "study stress, or difficult relationships at university — I'm genuinely here for that. "
            "What's making things hard right now?"
        )
    },
    {
        "patterns": [
            r"\b(self.harm|hurt myself|cutting|suicide|kill myself)\b",
            r"\b(don't want to (live|exist|be here))\b",
        ],
        "category": "self_harm",
        "response": (
            "I'm not the right resource for what you're describing, and I'm genuinely concerned.\n\n"
            "Please reach out to someone who can properly support you:\n"
            "- **iCall India**: 9152987821\n"
            "- **Crisis Text Line**: text HOME to 741741\n"
            "- **Vandrevala Foundation** (India, 24/7): 1860-2662-345\n\n"
            "You deserve real support from a real person. Please reach out."
        )
    },
    {
        "patterns": [
            r"\b(hack|exploit|bypass|jailbreak|ignore.*instruction|pretend.*you|act as if)\b",
            r"\b(ignore previous|disregard your|forget your rules|new persona)\b",
            r"\bdeveloper mode\b",
        ],
        "category": "prompt_injection",
        "response": (
            "I'm a focus science advisor — my role is fixed and I can't change it or ignore my guidelines.\n\n"
            "If you have a genuine question about focus, attention, productivity, or cognitive performance, "
            "I'm here and happy to help with that."
        )
    },
]

# ── Layer 2: Soft blocks (off-topic — redirect politely) ──────────────────────

SOFT_REDIRECT_PATTERNS = [
    {
        "patterns": [
            r"\b(write.*code|debug|programming|javascript|python|sql|algorithm)\b",
            r"\b(build.*app|create.*website|develop.*software)\b",
        ],
        "category": "coding",
        "response": (
            "Coding questions are outside my area — I'm specialized in focus and cognitive performance science.\n\n"
            "That said, if you're struggling to focus *while* coding or doing deep technical work, "
            "I can definitely help with that. Deep work research shows that programming requires "
            "the same kind of sustained attention as any cognitively demanding task — "
            "and the same strategies apply.\n\n"
            "Want strategies specifically for maintaining concentration during long coding sessions?"
        )
    },
    {
        "patterns": [
            r"\b(recipe|cook|food.*make|how.*bake)\b",
            r"\b(movie|show|series|netflix|watch)\b",
            r"\b(weather|stock|price|news|sports|score)\b",
        ],
        "category": "completely_off_topic",
        "response": (
            "That's outside what I can help with — I'm a focus science advisor.\n\n"
            "I can answer questions about attention, concentration, productivity, "
            "cognitive performance, study strategies, and evidence-based ways to "
            "improve your mental clarity.\n\n"
            "Is there anything about focus or attention you'd like to explore?"
        )
    },
    {
        "patterns": [
            r"\b(diet.*lose weight|weight loss|calorie|keto|intermittent fasting)\b",
        ],
        "category": "diet_off_topic",
        "response": (
            "I'm not a nutrition or weight loss advisor — but I can tell you how nutrition "
            "directly affects cognitive performance and focus.\n\n"
            "For example: blood sugar stability has a huge effect on attention. "
            "High-carb meals cause a glucose spike then crash — that afternoon slump you feel "
            "is partly a blood sugar crash. Meals combining protein, fats, and complex carbs "
            "produce more stable glucose and more stable attention.\n\n"
            "Want me to go deeper on how nutrition affects your focus specifically?"
        )
    },
]

# ── Layer 3: Harmful advice patterns in OUTPUT ────────────────────────────────
# Scan the LLM's response before sending it.
# These patterns suggest the LLM generated something we shouldn't pass on.

HARMFUL_OUTPUT_PATTERNS = [
    r"\b(take|use|try)\s+(adderall|ritalin|modafinil|amphetamine)\b",
    r"\b(recommend|suggest)\s+.*(illegal|controlled substance)\b",
    r"\b(self.medicate|self medicate)\b",
    r"\b(dosage|dose)\s+of\s+(adderall|ritalin|modafinil)\b",
]

# ── Layer 4: Soft warnings to APPEND to valid answers ─────────────────────────
# These don't block the response — they add a safety note at the end.
# Example: user asks about caffeine doses — valid question, but we add a note.

WARNING_TRIGGER_PATTERNS = [
    {
        "patterns": [r"\b(caffeine.*dose|how much caffeine|caffeine.*mg)\b"],
        "warning": (
            "\n\n*Note: Caffeine sensitivities vary significantly between individuals. "
            "If you have heart conditions, anxiety, or sleep difficulties, "
            "consult a doctor before adjusting your caffeine intake.*"
        )
    },
    {
        "patterns": [r"\b(adhd|attention deficit|hyperactivity)\b"],
        "warning": (
            "\n\n*Note: If you suspect ADHD, a proper clinical evaluation by a psychiatrist "
            "or psychologist is important. Focus strategies help everyone, but ADHD "
            "often benefits from professional diagnosis and treatment.*"
        )
    },
    {
        "patterns": [r"\b(sleep deprivation|no sleep|not sleeping|insomnia)\b"],
        "warning": (
            "\n\n*Note: Chronic sleep problems may have an underlying cause. "
            "If sleep difficulties persist, speaking to a doctor is worth considering.*"
        )
    },
]


# ── Main guardrail functions ───────────────────────────────────────────────────

def check_input(question: str) -> GuardrailResult:
    """
    Layer 1 + 2: Check the user's question before sending to the LLM.
    
    Returns GuardrailResult with allowed=False if we should block,
    or allowed=True with an optional warning to append later.
    
    HOW IT WORKS:
    We compile regex patterns and check them against the lowercased question.
    Hard blocks return immediately with a refusal message.
    Soft redirects return with a helpful redirect instead of blocking entirely.
    """
    q_lower = question.lower().strip()
    
    # Empty question
    if not q_lower:
        return GuardrailResult(
            allowed=False,
            message="Please type a question about focus, attention, or productivity.",
            category="empty"
        )
    
    # Too long (possible prompt injection attempt)
    if len(question) > 1500:
        return GuardrailResult(
            allowed=False,
            message="Your question is too long. Please keep it under 1500 characters.",
            category="too_long"
        )

    # Hard blocks — check first, most important
    for block in HARD_BLOCKED_PATTERNS:
        for pattern in block["patterns"]:
            if re.search(pattern, q_lower, re.IGNORECASE):
                return GuardrailResult(
                    allowed=False,
                    message=block["response"],
                    category=block["category"]
                )
    
    # Soft redirects
    for redirect in SOFT_REDIRECT_PATTERNS:
        for pattern in redirect["patterns"]:
            if re.search(pattern, q_lower, re.IGNORECASE):
                return GuardrailResult(
                    allowed=False,
                    message=redirect["response"],
                    category=redirect["category"]
                )
    
    # Check for warnings to attach later
    for warn in WARNING_TRIGGER_PATTERNS:
        for pattern in warn["patterns"]:
            if re.search(pattern, q_lower, re.IGNORECASE):
                return GuardrailResult(
                    allowed=True,
                    warning=warn["warning"],
                    category="warning_triggered"
                )
    
    # All clear
    return GuardrailResult(allowed=True)


def check_output(response: str) -> GuardrailResult:
    """
    Layer 3: Scan the LLM's response before sending to the user.
    
    If harmful patterns are detected in the output, we replace the
    response entirely rather than pass on bad advice.
    
    This is a safety net for cases where the LLM ignores its system prompt.
    """
    r_lower = response.lower()
    
    for pattern in HARMFUL_OUTPUT_PATTERNS:
        if re.search(pattern, r_lower, re.IGNORECASE):
            return GuardrailResult(
                allowed=False,
                message=(
                    "I generated a response that included content I shouldn't share. "
                    "For questions about medication or controlled substances, "
                    "please consult a qualified healthcare professional. "
                    "I'm happy to discuss evidence-based, non-pharmacological "
                    "focus strategies instead."
                ),
                category="harmful_output_detected"
            )
    
    return GuardrailResult(allowed=True)


def apply_warning(response: str, warning: Optional[str]) -> str:
    """Append a safety warning to an otherwise valid response."""
    if warning:
        return response + warning
    return response
