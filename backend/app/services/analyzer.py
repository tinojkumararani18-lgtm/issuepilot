from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

CATEGORIES = {
    "bug": ["bug", "error", "exception", "crash", "broken", "fails", "failure", "500", "traceback"],
    "feature": ["feature", "request", "enhancement", "support", "add", "allow", "would like"],
    "documentation": ["docs", "documentation", "readme", "typo", "guide", "example"],
    "question": ["question", "how do i", "how can i", "help", "usage", "why does"],
}
SEVERITY = {
    "critical": ["data loss", "security", "vulnerability", "production down", "outage", "rce"],
    "high": ["crash", "500", "cannot login", "blocks", "blocking", "corrupt"],
    "medium": ["fails", "error", "slow", "incorrect"],
}

def _score_keywords(text, mapping):
    lowered = text.lower()
    scores = {label: sum(1 for word in words if word in lowered) for label, words in mapping.items()}
    label, score = max(scores.items(), key=lambda item: item[1])
    if score == 0:
        return "other", 0.45
    total = sum(scores.values())
    return label, min(0.95, 0.55 + score / max(total, 1) * 0.4)

def classify(title, body):
    return _score_keywords(f"{title}\n{body}", CATEGORIES)

def severity_for(title, body):
    label, _ = _score_keywords(f"{title}\n{body}", SEVERITY)
    return label if label != "other" else "low"

def priority_for(category, severity, title):
    text = title.lower()
    if severity == "critical" or "urgent" in text or "security" in text:
        return "critical"
    if severity == "high":
        return "high"
    if category in {"bug", "feature"}:
        return "medium"
    return "low"

def duplicate_matches(title, body, existing, threshold=0.55):
    if not existing:
        return []
    texts = [f"{item['title']}\n{item.get('body', '')}" for item in existing]
    matrix = TfidfVectorizer(stop_words="english").fit_transform(texts + [f"{title}\n{body}"])
    scores = cosine_similarity(matrix[-1], matrix[:-1]).ravel()
    matches = [
        {"title": existing[i]["title"], "score": round(float(score), 3)}
        for i, score in enumerate(scores) if score >= threshold
    ]
    return sorted(matches, key=lambda x: x["score"], reverse=True)[:5]

def suggested_reply(category):
    replies = {
        "bug": "Thanks for reporting this. We’ll reproduce the issue and review the environment details. If possible, please include the smallest reproducible example and logs.",
        "feature": "Thanks for the feature request. We’ll review the use case and consider it against the project roadmap.",
        "documentation": "Thanks for spotting this. We’ll review the documentation and improve the relevant section.",
        "question": "Thanks for the question. We’ll clarify the usage and update the documentation if the answer is broadly useful.",
    }
    return replies.get(category, "Thanks for opening this issue. We’ll review it and follow up with next steps.")

def analyze(title, body, existing=None, threshold=0.55):
    category, confidence = classify(title, body)
    severity = severity_for(title, body)
    priority = priority_for(category, severity, title)
    return {
        "category": category,
        "priority": priority,
        "severity": severity,
        "confidence": round(confidence, 3),
        "duplicate_matches": duplicate_matches(title, body, existing or [], threshold),
        "suggested_reply": suggested_reply(category),
    }
