from pydantic import BaseModel, Field

class IssueInput(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    body: str = ""

class DuplicateMatch(BaseModel):
    title: str
    score: float

class AnalysisResult(BaseModel):
    category: str
    priority: str
    severity: str
    confidence: float
    duplicate_matches: list[DuplicateMatch] = []
    suggested_reply: str

class GitHubIssueRequest(BaseModel):
    owner: str
    repo: str
    issue_number: int
