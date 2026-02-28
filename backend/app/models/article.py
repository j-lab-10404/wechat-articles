"""Article model."""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from ..database import Base


class Article(Base):
    """文章模型."""

    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(500), nullable=False)
    content = Column(Text)  # HTML 全文
    content_text = Column(Text)  # 纯文本
    url = Column(Text, unique=True)
    author = Column(String(255))
    cover_image = Column(Text)
    published_at = Column(DateTime(timezone=True))
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())

    # 用户交互
    is_favorite = Column(Boolean, default=False, index=True)
    labels = Column(JSONB, default=[])  # 标签列表，AI 自动 + 用户手动

    # AI 分析
    article_type = Column(String(50), index=True)  # paper_review, dataset, tool, tutorial, news, other
    summary = Column(Text)
    keywords = Column(JSONB, default=[])
    ai_labels = Column(JSONB, default=[])  # AI 建议的标签（合并到 labels）

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    account = relationship("Account", back_populates="articles")
    analysis = relationship("ArticleAnalysis", back_populates="article", uselist=False, cascade="all, delete-orphan")
    papers = relationship("Paper", back_populates="source_article", cascade="all, delete-orphan")
    datasets = relationship("Dataset", back_populates="source_article", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_articles_published_at', published_at.desc()),
        Index('idx_articles_type', article_type),
    )

    def __repr__(self):
        return f"<Article(id={self.id}, title='{self.title[:30]}...')>"
