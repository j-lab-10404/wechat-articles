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


@router.get("/{article_id}", response_model=schemas.ArticleDetail)
async def get_article(article_id: int, db: Session = Depends(get_db)):
    """获取文章详情（含分析、论文、数据集）."""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


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
    用户分享文章链接 → 从 WeWe-RSS 获取全文 → AI 分析 → 入库.

    流程：
    1. 检查是否已添加过
    2. 从 WeWe-RSS 获取文章全文
    3. 保存文章
    4. AI 分析（分类、标签、论文/数据集提取）
    5. 保存分析结果
    """
    url = request.url.strip()

    # 1. 检查重复
    existing = db.query(Article).filter(Article.url == url).first()
    if existing:
        raise HTTPException(status_code=400, detail="文章已存在")

    # 2. 从 WeWe-RSS 获取全文
    rss = RSSService()
    article_data = await rss.get_article_content(url)

    if not article_data or not article_data.get("content_text"):
        # WeWe-RSS 中没找到，可能公众号还没订阅
        # 尝试添加订阅
        try:
            await rss.add_feed(url)
            # 等一下再试
            import asyncio
            await asyncio.sleep(3)
            article_data = await rss.get_article_content(url)
        except Exception as e:
            print(f"Auto-subscribe failed: {e}")

    # 3. 保存文章
    title = (article_data or {}).get("title", "未知标题")
    content_html = (article_data or {}).get("content_html", "")
    content_text = (article_data or {}).get("content_text", "")
    author = (article_data or {}).get("author", "")
    published_at = (article_data or {}).get("published_at")

    db_article = Article(
        title=title,
        content=content_html,
        content_text=content_text,
        url=url,
        author=author,
        published_at=published_at,
        is_favorite=True,  # 用户主动分享的，默认收藏
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
    }

    # 4. AI 分析
    if request.auto_analyze and content_text:
        try:
            ai = AIService()
            analysis = await ai.analyze_article(title, content_text)

            # 更新文章字段
            db_article.article_type = analysis.get("article_type", "other")
            db_article.summary = analysis.get("summary", "")
            db_article.keywords = analysis.get("keywords", [])
            db_article.labels = analysis.get("labels", [])
            db_article.ai_labels = analysis.get("labels", [])

            # 保存 ArticleAnalysis
            db_analysis = ArticleAnalysis(
                article_id=db_article.id,
                summary=analysis.get("summary"),
                keywords=analysis.get("keywords"),
                category_confidence=0.0,
                paper_info=analysis.get("papers"),
                tool_info=None,
                news_info=None,
            )
            db.add(db_analysis)

            # 5. 保存论文信息
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
                # 尝试构建 PDF 链接
                if p.get("arxiv_id"):
                    paper.pdf_url = f"https://arxiv.org/pdf/{p['arxiv_id']}"
                    paper.source_url = f"https://arxiv.org/abs/{p['arxiv_id']}"
                elif p.get("doi"):
                    paper.source_url = f"https://doi.org/{p['doi']}"
                    paper.pdf_url = f"https://sci-hub.se/{p['doi']}"
                db.add(paper)

            # 6. 保存数据集信息
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
