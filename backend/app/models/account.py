"""Account model."""
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Account(Base):
    """公众号模型."""
    
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    weread_id = Column(String(255), unique=True, index=True)
    avatar = Column(Text)
    description = Column(Text)
    feed_url = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    articles = relationship("Article", back_populates="account")
    
    def __repr__(self):
        return f"<Account(id={self.id}, name='{self.name}')>"
