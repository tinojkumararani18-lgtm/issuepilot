import hashlib
import hmac
import json
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.db import get_db
from app.models import IssueRecord
from app.schemas import AnalysisResult, GitHubIssueRequest, IssueInput
from app.services.analyzer import analyze
from app.services.github import get_issue, list_issues
from app.services.llm import llm_analyze

router = APIRouter(prefix="/api")

def existing_issue_dicts(db):
    return [{"title": x.title, "body": x.body}
            for x in db.query(IssueRecord).order_by(IssueRecord.id.desc()).limit(200).all()]

def run_analysis(title, body, db):
    settings = get_settings()
    result = analyze(title, body, existing_issue_dicts(db), settings.duplicate_threshold)
    enhanced = llm_analyze(title, body)
    if enhanced:
        result.update({
            "category": enhanced["category"],
            "priority": enhanced["priority"],
            "severity": enhanced["severity"],
            "confidence": float(enhanced["confidence"]),
            "suggested_reply": enhanced["suggested_reply"],
        })
    return result

@router.post("/analyze", response_model=AnalysisResult)
def analyze_issue(payload: IssueInput, db: Session = Depends(get_db)):
    return run_analysis(payload.title, payload.body, db)

@router.get("/github/issues")
async def github_issues(owner: str, repo: str, state: str = "open"):
    try:
        items = await list_issues(owner, repo, state)
        return [
            {"number": x["number"], "title": x["title"], "body": x.get("body") or "",
             "html_url": x["html_url"], "state": x["state"]}
            for x in items if "pull_request" not in x
        ]
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"GitHub request failed: {exc}") from exc

@router.post("/github/analyze", response_model=AnalysisResult)
async def analyze_github_issue(payload: GitHubIssueRequest, db: Session = Depends(get_db)):
    try:
        issue = await get_issue(payload.owner, payload.repo, payload.issue_number)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"GitHub request failed: {exc}") from exc
    result = run_analysis(issue["title"], issue.get("body") or "", db)
    record = IssueRecord(
        github_id=issue.get("id"), owner=payload.owner, repo=payload.repo,
        issue_number=payload.issue_number, title=issue["title"], body=issue.get("body") or "",
        category=result["category"], priority=result["priority"], severity=result["severity"],
        confidence=result["confidence"],
    )
    db.merge(record)
    db.commit()
    return result

@router.post("/webhooks/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    settings = get_settings()
    raw = await request.body()
    expected = "sha256=" + hmac.new(settings.github_webhook_secret.encode(), raw, hashlib.sha256).hexdigest()
    if not x_hub_signature_256 or not hmac.compare_digest(expected, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    event = request.headers.get("X-GitHub-Event", "")
    payload = json.loads(raw.decode("utf-8"))

    if event == "issues" and payload.get("action") in {"opened", "edited", "reopened"}:
        issue = payload["issue"]
        repo = payload["repository"]
        result = run_analysis(issue["title"], issue.get("body") or "", db)
        record = IssueRecord(
            github_id=issue.get("id"), owner=repo["owner"]["login"], repo=repo["name"],
            issue_number=issue["number"], title=issue["title"], body=issue.get("body") or "",
            category=result["category"], priority=result["priority"], severity=result["severity"],
            confidence=result["confidence"],
        )
        db.merge(record)
        db.commit()
        return {"processed": True, "analysis": result}

    return {"processed": False, "event": event}
