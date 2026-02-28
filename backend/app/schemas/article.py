"""Article schemas."""
from pydantic import BaseModel, ConfigDict
from typing import Optional, Any
from datetime import datetime


class ArticleBase(BaseModel):
    """Base article schema."""
    title: str
    url: Optional[str] = None
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    article_type: Optional[str] = None
    summary: Optional[str] = None
    labels: Optional[list[str]] = []
    keywords: Optional[list[str]] = []


class ArticleCreate(ArticleBase):
    """Schema for creating article."""
    content: Optional[str] = None
    content_text: Optional[str] = None
    account_id: Optional[int] = None


class ArticleUpdate(BaseModel):
    """Schema for updating article."""
    title: Optional[str] = None
    is_favorite: Optional[bool] = None
    labels: Optional[list[str]] = None
    article_type: Optional[str] = None


class Article(ArticleBase):
    """Schema for article response."""
    id: int
    account_id: Optional[int] = None
    is_favorite: bool = False
    cover_image: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ArticleDetail(Article):
    """Schema for article detail with analysis, papers, datasets."""
    content: Optional[str] = None
    content_text: Optional[str] = None
    ai_labels: Optional[list[str]] = []
    analysis: Optional[Any] = None
    papers: Optional[list[Any]] = []
    datasets: Optional[list[Any]] = []

    model_config = ConfigDict(from_attributes=True)


class ArticleList(BaseModel):
    """Schema for article list response."""
    total: int
    items: list[Article]
