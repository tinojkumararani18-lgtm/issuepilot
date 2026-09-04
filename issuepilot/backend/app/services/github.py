import httpx
from app.core.config import get_settings

BASE_URL = "https://api.github.com"

def _headers():
    settings = get_settings()
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"
    return headers

async def list_issues(owner, repo, state="open"):
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(
            f"{BASE_URL}/repos/{owner}/{repo}/issues",
            params={"state": state, "per_page": 30},
            headers=_headers(),
        )
        response.raise_for_status()
        return response.json()

async def get_issue(owner, repo, number):
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(
            f"{BASE_URL}/repos/{owner}/{repo}/issues/{number}",
            headers=_headers(),
        )
        response.raise_for_status()
        return response.json()
