"""Paper model - 论文信息."""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from ..database import Base


class Paper(Base):
    """论文模型 - 从论文解读类文章中提取."""

    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    source_article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)

    # 论文基本信息
    title = Column(String(500), nullable=False)
    title_cn = Column(String(500))  # 中文标题
    authors = Column(JSONB, default=[])  # ["Author1", "Author2"]
    journal = Column(String(255))  # 期刊/会议名称
    year = Column(Integer)
    doi = Column(String(255), index=True)
    arxiv_id = Column(String(50))
    pubmed_id = Column(String(50))

    # 论文内容
    abstract = Column(Text)
    main_findings = Column(Text)  # AI 提取的主要发现

    # 原文获取
    pdf_url = Column(Text)  # 原文 PDF 链接（arXiv / Sci-Hub / PMC）
    source_url = Column(Text)  # 论文原始页面链接

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    source_article = relationship("Article", back_populates="papers")

    def __repr__(self):
        return f"<Paper(id={self.id}, title='{self.title[:30]}...')>"
