import json
from app.core.config import get_settings

def llm_analyze(title, body):
    settings = get_settings()
    if not settings.openai_api_key or not settings.openai_model:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.openai_api_key)
        prompt = f'''Analyze this GitHub issue and return ONLY valid JSON with:
category (bug|feature|documentation|question|other),
priority (critical|high|medium|low),
severity (critical|high|medium|low),
confidence (0 to 1),
suggested_reply (short maintainer reply).

Title:
{title}

Body:
{body}
'''
        response = client.responses.create(model=settings.openai_model, input=prompt)
        data = json.loads(response.output_text.strip())
        required = {"category", "priority", "severity", "confidence", "suggested_reply"}
        return data if required.issubset(data) else None
    except Exception:
        return None
