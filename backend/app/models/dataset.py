"""Dataset model - 公开数据集信息."""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from ..database import Base


class Dataset(Base):
    """公开数据集模型 - 从数据集分享类文章中提取."""

    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    source_article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)

    # 数据集基本信息
    name = Column(String(500), nullable=False)
    description = Column(Text)  # 数据集简介
    data_type = Column(String(100))  # 数据类型：图像、文本、音频等
    scale = Column(String(255))  # 数据规模：如 "10万张图像"
    domain = Column(String(255))  # 所属领域：医学影像、NLP 等
    license = Column(String(255))  # 许可证

    # 获取方式
    download_url = Column(Text)  # 下载链接
    access_method = Column(Text)  # 获取方式说明（申请流程等）
    tutorial = Column(Text)  # 详细获取教程

    # 关联论文
    related_papers = Column(JSONB, default=[])  # 相关论文 DOI 或标题列表

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    source_article = relationship("Article", back_populates="datasets")

    def __repr__(self):
        return f"<Dataset(id={self.id}, name='{self.name[:30]}...')>"
