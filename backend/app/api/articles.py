"""Article API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from ..database import get_db
from ..models import Article, ArticleAnalysis, Account, Paper, Dataset
from ..schemas import article as schemas
from ..services.ai_service import AIService
from ..services.rss_service import RSSService

router = APIRouter()


# ── Request Models ──────────────────────────────────────────────

class AddArticleRequest(BaseModel):
    """用户分享文章链接."""
    url: str
    auto_analyze: bool = True


class UpdateLabelsRequest(BaseModel):
    """手动修改标签."""
    labels: list[str]


# ── CRUD ────────────────────────────────────────────────────────

@router.get("/", response_model=schemas.ArticleList)
async def get_articles(
    article_type: Optional[str] = None,
    label: Optional[str] = None,
    is_favorite: Optional[bool] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """获取文章列表，支持按类型、标签、收藏筛选."""
    query = db.query(Article)

    if article_type:
        query = query.filter(Article.article_type == article_type)
    if is_favorite is not None:
        query = query.filter(Article.is_favorite == is_favorite)
    if label:
        # JSONB 包含查询
        query = query.filter(Article.labels.contains([label]))

    total = query.count()
    articles = query.order_by(Article.created_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "items": articles}


@router.get("/labels")
async def get_all_labels(db: Session = Depends(get_db)):
    """获取所有已使用的标签及其计数."""
    from sqlalchemy import text
    result = db.execute(text("""
        SELECT label, COUNT(*) as count
        FROM articles, jsonb_array_elements_text(COALESCE(labels, '[]'::jsonb)) AS label
        GROUP BY label
        ORDER BY count DESC
    """))
    return [{"label": row[0], "count": row[1]} for row in result]


@router.get("/{article_id}")
async def get_article(article_id: int, db: Session = Depends(get_db)):
    """获取文章详情（含分析、论文、数据集）."""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Manual serialization to avoid Pydantic issues with relationships
    result = {
        "id": article.id,
        "title": article.title,
        "url": article.url,
        "author": article.author,
        "published_at": article.published_at.isoformat() if article.published_at else None,
        "article_type": article.article_type,
        "summary": article.summary,
        "labels": article.labels or [],
        "keywords": article.keywords or [],
        "ai_labels": article.ai_labels or [],
        "is_favorite": article.is_favorite or False,
        "content": article.content,
        "content_text": article.content_text,
        "created_at": article.created_at.isoformat() if article.created_at else None,
        "updated_at": article.updated_at.isoformat() if article.updated_at else None,
        "papers": [],
        "datasets": [],
        "analysis": None,
    }

    if article.papers:
        for p in article.papers:
            result["papers"].append({
                "id": p.id, "title": p.title, "title_cn": p.title_cn,
                "authors": p.authors or [], "journal": p.journal,
                "year": p.year, "doi": p.doi, "arxiv_id": p.arxiv_id,
                "abstract": p.abstract, "main_findings": p.main_findings,
                "pdf_url": p.pdf_url, "source_url": p.source_url,
            })

    if article.datasets:
        for d in article.datasets:
            result["datasets"].append({
                "id": d.id, "name": d.name, "description": d.description,
                "data_type": d.data_type, "scale": d.scale, "domain": d.domain,
                "download_url": d.download_url, "access_method": d.access_method,
                "tutorial": d.tutorial, "related_papers": d.related_papers or [],
            })

    if article.analysis:
        a = article.analysis
        result["analysis"] = {
            "id": a.id, "summary": a.summary, "keywords": a.keywords,
            "category_confidence": a.category_confidence,
        }

    return result


@router.delete("/{article_id}")
async def delete_article(article_id: int, db: Session = Depends(get_db)):
    """删除文章."""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    db.delete(article)
    db.commit()
    return {"message": "Article deleted"}


# ── 核心：添加文章 ─────────────────────────────────────────────

@router.post("/add")
async def add_article(request: AddArticleRequest, db: Session = Depends(get_db)):
    """
    添加文章：先保存 URL，然后尝试获取内容和 AI 分析。
    如果内容获取超时，返回文章 ID，前端可调用 /fetch-content 重试。
    """
    url = request.url.strip()

    existing = db.query(Article).filter(Article.url == url).first()
    if existing:
        raise HTTPException(status_code=400, detail="文章已存在")

    # 尝试从 WeWe-RSS 获取内容
    rss = RSSService()
    article_data = None
    try:
        article_data = await rss.get_article_content(url)
    except Exception as e:
        print(f"Content fetch failed: {e}")

    title = (article_data or {}).get("title", "")
    content_html = (article_data or {}).get("content_html", "")
    content_text = (article_data or {}).get("content_text", "")
    author = (article_data or {}).get("author", "")
    published_at = (article_data or {}).get("published_at")

    db_article = Article(
        title=title or "待获取",
        content=content_html,
        content_text=content_text,
        url=url,
        author=author,
        published_at=published_at,
        is_favorite=True,
        labels=[],
    )
    db.add(db_article)
    db.commit()
    db.refresh(db_article)

    result = {
        "id": db_article.id,
        "title": db_article.title,
        "url": db_article.url,
        "content_length": len(content_text),
        "analysis_status": "skipped",
        "need_fetch": not bool(content_text),
    }

    # AI 分析（仅在有内容时）
    if request.auto_analyze and content_text:
        result.update(await _do_analysis(db, db_article, content_text))

    return result


@router.post("/{article_id}/fetch-content")
async def fetch_content(article_id: int, db: Session = Depends(get_db)):
    """从 WeWe-RSS 获取文章内容（用于重试）."""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    rss = RSSService()
    article_data = await rss.get_article_content(article.url)

    if not article_data or not article_data.get("content_text"):
        raise HTTPException(status_code=404, detail="WeWe-RSS 中未找到文章内容")

    article.title = article_data.get("title") or article.title
    article.content = article_data.get("content_html", "")
    article.content_text = article_data.get("content_text", "")
    article.author = article_data.get("author") or article.author
    article.published_at = article_data.get("published_at") or article.published_at
    db.commit()
    db.refresh(article)

    return {
        "id": article.id,
        "title": article.title,
        "content_length": len(article.content_text or ""),
    }


async def _do_analysis(db: Session, db_article: Article, content_text: str) -> dict:
    """执行 AI 分析并保存结果."""
    result = {}
    try:
        ai = AIService()
        analysis = await ai.analyze_article(db_article.title, content_text)

        db_article.article_type = analysis.get("article_type", "other")
        db_article.summary = analysis.get("summary", "")
        db_article.keywords = analysis.get("keywords", [])
        db_article.labels = analysis.get("labels", [])
        db_article.ai_labels = analysis.get("labels", [])

        db_analysis = ArticleAnalysis(
            article_id=db_article.id,
            summary=analysis.get("summary"),
            keywords=analysis.get("keywords"),
            category_confidence=0.0,
            paper_info=analysis.get("papers"),
        )
        db.add(db_analysis)

        for p in analysis.get("papers", []):
            paper = Paper(
                source_article_id=db_article.id,
                title=p.get("title", "Unknown"),
                title_cn=p.get("title_cn"),
                authors=p.get("authors", []),
                journal=p.get("journal"),
                year=p.get("year"),
                doi=p.get("doi"),
                arxiv_id=p.get("arxiv_id"),
                abstract=p.get("abstract"),
                main_findings=p.get("main_findings"),
            )
            if p.get("arxiv_id"):
                paper.pdf_url = f"https://arxiv.org/pdf/{p['arxiv_id']}"
                paper.source_url = f"https://arxiv.org/abs/{p['arxiv_id']}"
            elif p.get("doi"):
                paper.source_url = f"https://doi.org/{p['doi']}"
                paper.pdf_url = f"https://sci-hub.se/{p['doi']}"
            db.add(paper)

        for d in analysis.get("datasets", []):
            dataset = Dataset(
                source_article_id=db_article.id,
                name=d.get("name", "Unknown"),
                description=d.get("description"),
                data_type=d.get("data_type"),
                scale=d.get("scale"),
                domain=d.get("domain"),
                download_url=d.get("download_url"),
                access_method=d.get("access_method"),
                tutorial=d.get("tutorial"),
                related_papers=d.get("related_papers", []),
            )
            db.add(dataset)

        db.commit()
        db.refresh(db_article)

        result["analysis_status"] = "completed"
        result["article_type"] = db_article.article_type
        result["labels"] = db_article.labels
        result["summary"] = db_article.summary
        result["papers_count"] = len(analysis.get("papers", []))
        result["datasets_count"] = len(analysis.get("datasets", []))

    except Exception as e:
        print(f"AI analysis failed: {e}")
        import traceback
        traceback.print_exc()
        result["analysis_status"] = "failed"
        result["analysis_error"] = str(e)

    return result


# ── 标签管理 ────────────────────────────────────────────────────

@router.put("/{article_id}/labels")
async def update_labels(article_id: int, request: UpdateLabelsRequest, db: Session = Depends(get_db)):
    """手动修改文章标签."""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    article.labels = request.labels
    db.commit()
    db.refresh(article)
    return {"id": article.id, "labels": article.labels}


@router.post("/{article_id}/labels/add")
async def add_label(article_id: int, label: str = Query(...), db: Session = Depends(get_db)):
    """给文章添加一个标签."""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    current = list(article.labels or [])
    if label not in current:
        current.append(label)
        article.labels = current
        db.commit()
        db.refresh(article)
    return {"id": article.id, "labels": article.labels}


@router.delete("/{article_id}/labels/{label}")
async def remove_label(article_id: int, label: str, db: Session = Depends(get_db)):
    """移除文章的一个标签."""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    current = list(article.labels or [])
    if label in current:
        current.remove(label)
        article.labels = current
        db.commit()
        db.refresh(article)
    return {"id": article.id, "labels": article.labels}


# ── 收藏 ────────────────────────────────────────────────────────

@router.post("/{article_id}/favorite")
async def toggle_favorite(article_id: int, db: Session = Depends(get_db)):
    """切换收藏状态."""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    article.is_favorite = not article.is_favorite
    db.commit()
    db.refresh(article)
    return {"id": article.id, "is_favorite": article.is_favorite}


# ── 重新分析 ────────────────────────────────────────────────────

@router.post("/{article_id}/analyze")
async def analyze_article(article_id: int, db: Session = Depends(get_db)):
    """重新 AI 分析文章."""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    if not article.content_text:
        raise HTTPException(status_code=400, detail="文章没有内容，无法分析")

    ai = AIService()
    analysis = await ai.analyze_article(article.title, article.content_text)

    # 更新文章
    article.article_type = analysis.get("article_type", "other")
    article.summary = analysis.get("summary", "")
    article.keywords = analysis.get("keywords", [])
    article.labels = analysis.get("labels", [])
    article.ai_labels = analysis.get("labels", [])

    # 删除旧分析
    old_analysis = db.query(ArticleAnalysis).filter(ArticleAnalysis.article_id == article_id).first()
    if old_analysis:
        db.delete(old_analysis)

    # 删除旧论文和数据集
    db.query(Paper).filter(Paper.source_article_id == article_id).delete()
    db.query(Dataset).filter(Dataset.source_article_id == article_id).delete()

    # 保存新分析
    db_analysis = ArticleAnalysis(
        article_id=article.id,
        summary=analysis.get("summary"),
        keywords=analysis.get("keywords"),
    )
    db.add(db_analysis)

    for p in analysis.get("papers", []):
        paper = Paper(
            source_article_id=article.id,
            title=p.get("title", "Unknown"),
            title_cn=p.get("title_cn"),
            authors=p.get("authors", []),
            journal=p.get("journal"),
            year=p.get("year"),
            doi=p.get("doi"),
            arxiv_id=p.get("arxiv_id"),
            abstract=p.get("abstract"),
            main_findings=p.get("main_findings"),
        )
        if p.get("arxiv_id"):
            paper.pdf_url = f"https://arxiv.org/pdf/{p['arxiv_id']}"
            paper.source_url = f"https://arxiv.org/abs/{p['arxiv_id']}"
        elif p.get("doi"):
            paper.source_url = f"https://doi.org/{p['doi']}"
            paper.pdf_url = f"https://sci-hub.se/{p['doi']}"
        db.add(paper)

    for d in analysis.get("datasets", []):
        dataset = Dataset(
            source_article_id=article.id,
            name=d.get("name", "Unknown"),
            description=d.get("description"),
            data_type=d.get("data_type"),
            scale=d.get("scale"),
            domain=d.get("domain"),
            download_url=d.get("download_url"),
            access_method=d.get("access_method"),
            tutorial=d.get("tutorial"),
            related_papers=d.get("related_papers", []),
        )
        db.add(dataset)

    db.commit()

    return {
        "message": "分析完成",
        "article_type": article.article_type,
        "labels": article.labels,
        "summary": article.summary,
    }


# ── 搜索 ────────────────────────────────────────────────────────

@router.get("/search/", response_model=schemas.ArticleList)
async def search_articles(
    q: str = Query(..., min_length=1),
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """搜索文章."""
    query = db.query(Article).filter(
        (Article.title.ilike(f"%{q}%")) | (Article.content_text.ilike(f"%{q}%"))
    )
    total = query.count()
    articles = query.order_by(Article.created_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "items": articles}
