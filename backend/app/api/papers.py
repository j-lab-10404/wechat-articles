"""Paper API endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Paper

router = APIRouter()


@router.get("/")
async def list_papers(
    skip: int = 0,
    limit: int = 20,
    q: str = Query(None),
    db: Session = Depends(get_db),
):
    """获取论文列表."""
    query = db.query(Paper)
    if q:
        query = query.filter(
            (Paper.title.ilike(f"%{q}%")) | (Paper.title_cn.ilike(f"%{q}%"))
        )
    total = query.count()
    items = query.order_by(Paper.created_at.desc()).offset(skip).limit(limit).all()
    return {
        "total": total,
        "items": [
            {
                "id": p.id,
                "title": p.title,
                "title_cn": p.title_cn,
                "authors": p.authors,
                "journal": p.journal,
                "year": p.year,
                "doi": p.doi,
                "arxiv_id": p.arxiv_id,
                "abstract": p.abstract,
                "main_findings": p.main_findings,
                "pdf_url": p.pdf_url,
                "source_url": p.source_url,
                "source_article_id": p.source_article_id,
                "created_at": p.created_at,
            }
            for p in items
        ],
    }
