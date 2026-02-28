"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import init_db
from .api import accounts, articles, knowledge

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(accounts.router, prefix="/api/accounts", tags=["accounts"])
app.include_router(articles.router, prefix="/api/articles", tags=["articles"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["knowledge"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "wewe_rss": settings.WEWE_RSS_URL,
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
