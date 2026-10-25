from fastapi import FastAPI

from datejar.config import settings

docs_enabled = settings.environment == "dev"

app = FastAPI(
    title="DateJar API",
    description="A self-hosted date idea jar for couples — add ideas, filter by mood, weather and budget, and draw your next date..",
    version="0.1.0",
    docs_url="/docs" if docs_enabled else None,
    redoc_url="/redoc" if docs_enabled else None,
    openapi_url="/openapi.json" if docs_enabled else None,
)


@app.get("/")
def root():
    return {"message": "Welcome to DateJar Mike!"}


@app.get("/healthz")
def health_check():
    return {"status": "healthy"}
