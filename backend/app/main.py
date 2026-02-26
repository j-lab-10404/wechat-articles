"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import init_db
from .api import accounts, articles, knowledge

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(accounts.router, prefix="/api/accounts", tags=["accounts"])
app.include_router(articles.router, prefix="/api/articles", tags=["articles"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["knowledge"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/debug/config")
async def debug_config():
    """Debug endpoint to check configuration (DO NOT use in production)."""
    return {
        "scraperapi_configured": bool(settings.SCRAPERAPI_KEY),
        "scraperapi_key_length": len(settings.SCRAPERAPI_KEY) if settings.SCRAPERAPI_KEY else 0,
        "scraperapi_key_preview": settings.SCRAPERAPI_KEY[:10] + "..." if settings.SCRAPERAPI_KEY else "NOT SET",
        "openai_configured": bool(settings.OPENAI_API_KEY),
        "openai_base_url": settings.OPENAI_BASE_URL,
        "openai_model": settings.OPENAI_MODEL,
        "database_configured": bool(settings.DATABASE_URL),
        "cors_origins": settings.cors_origins_list,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
