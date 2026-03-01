"""Dataset API endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Dataset

router = APIRouter()


@router.get("/")
async def list_datasets(
    skip: int = 0,
    limit: int = 20,
    q: str = Query(None),
    db: Session = Depends(get_db),
):
    """获取数据集列表."""
    query = db.query(Dataset)
    if q:
        query = query.filter(
            (Dataset.name.ilike(f"%{q}%")) | (Dataset.description.ilike(f"%{q}%"))
        )
    total = query.count()
    items = query.order_by(Dataset.created_at.desc()).offset(skip).limit(limit).all()
    return {
        "total": total,
        "items": [
            {
                "id": d.id,
                "name": d.name,
                "description": d.description,
                "data_type": d.data_type,
                "scale": d.scale,
                "domain": d.domain,
                "download_url": d.download_url,
                "access_method": d.access_method,
                "tutorial": d.tutorial,
                "related_papers": d.related_papers,
                "source_article_id": d.source_article_id,
                "created_at": d.created_at,
            }
            for d in items
        ],
    }
