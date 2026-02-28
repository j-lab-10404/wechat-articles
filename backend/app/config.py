"""Application configuration."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # wewe-rss
    WEWE_RSS_URL: str = "https://wewe-rss-production-d5fc.up.railway.app"
    WEWE_RSS_AUTH_CODE: str = ""
    
    # OpenAI
    OPENAI_API_KEY: str = ""  # 改为可选，默认空字符串
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"  # 支持自定义，如 DeepSeek
    
    # ScraperAPI (optional, for web scraping)
    SCRAPERAPI_KEY: str = ""  # ScraperAPI key for bypassing anti-scraping
    
    # Application
    APP_NAME: str = "WeChat Articles Knowledge Base"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    # File storage
    MEDIA_ROOT: str = "./media"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    
    # Sync settings
    SYNC_INTERVAL_MINUTES: int = 60
    ARTICLES_PER_SYNC: int = 50
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
