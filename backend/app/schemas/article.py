"""Article schemas."""
from pydantic import BaseModel, ConfigDict
from typing import Optional, Any
from datetime import datetime


class PaperSchema(BaseModel):
    id: int
    title: str
    title_cn: Optional[str] = None
    authors: Optional[list[str]] = []
    journal: Optional[str] = None
    year: Optional[int] = None
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    pubmed_id: Optional[str] = None
    abstract: Optional[str] = None
    main_findings: Optional[str] = None
    pdf_url: Optional[str] = None
    source_url: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DatasetSchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    data_type: Optional[str] = None
    scale: Optional[str] = None
    domain: Optional[str] = None
    license: Optional[str] = None
    download_url: Optional[str] = None
    access_method: Optional[str] = None
    tutorial: Optional[str] = None
    related_papers: Optional[list[str]] = []
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AnalysisSchema(BaseModel):
    id: int
    summary: Optional[str] = None
    keywords: Optional[list[str]] = []
    category_confidence: Optional[float] = None
    paper_info: Optional[Any] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ArticleBase(BaseModel):
    title: str
    url: Optional[str] = None
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    article_type: Optional[str] = None
    summary: Optional[str] = None
    labels: Optional[list[str]] = []
    keywords: Optional[list[str]] = []


class ArticleCreate(ArticleBase):
    content: Optional[str] = None
    content_text: Optional[str] = None
    account_id: Optional[int] = None


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    is_favorite: Optional[bool] = None
    labels: Optional[list[str]] = None
    article_type: Optional[str] = None


class Article(ArticleBase):
    id: int
    account_id: Optional[int] = None
    is_favorite: bool = False
    cover_image: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ArticleDetail(Article):
    content: Optional[str] = None
    content_text: Optional[str] = None
    ai_labels: Optional[list[str]] = []
    analysis: Optional[AnalysisSchema] = None
    papers: Optional[list[PaperSchema]] = []
    datasets: Optional[list[DatasetSchema]] = []

    model_config = ConfigDict(from_attributes=True)


class ArticleList(BaseModel):
    total: int
    items: list[Article]
