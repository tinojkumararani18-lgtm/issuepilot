from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.config import get_settings
from app.db import Base, engine

settings = get_settings()
Base.metadata.create_all(bind=engine)

app = FastAPI(title="IssuePilot API", version="1.0.0",
              description="AI-assisted GitHub issue triage platform.")

origins = [x.strip() for x in settings.cors_origins.split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins or ["*"],
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(router)

@app.get("/")
def root():
    return {"name": "IssuePilot", "status": "ok"}

@app.get("/health")
def health():
    return {"status": "healthy"}
