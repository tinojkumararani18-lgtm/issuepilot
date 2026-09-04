from app.services.analyzer import analyze, classify, duplicate_matches

def test_bug_classification():
    category, confidence = classify("Application crashes", "The server throws a traceback and returns 500.")
    assert category == "bug"
    assert confidence > 0.5

def test_security_priority():
    result = analyze("Security vulnerability", "Possible remote code execution vulnerability.")
    assert result["priority"] == "critical"
    assert result["severity"] == "critical"

def test_duplicate_detection():
    existing = [
        {"title": "Login fails with 500", "body": "Users receive an internal server error."},
        {"title": "Improve README", "body": "The setup docs need a small update."},
    ]
    matches = duplicate_matches("Login returns a 500 error",
                                "Users get an internal server error when logging in.",
                                existing, threshold=0.2)
    assert matches
