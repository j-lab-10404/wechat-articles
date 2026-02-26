"""Article API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..models import Article, ArticleAnalysis, Account
from ..schemas import article as schemas
from ..services.ai_service import AIService
from ..services.wechat_scraper import WeChatScraper
from pydantic import BaseModel

router = APIRouter()


class ScrapeArticleRequest(BaseModel):
    """Request model for scraping article."""
    url: str
    account_id: Optional[int] = None
    auto_analyze: bool = True


@router.get("/", response_model=schemas.ArticleList)
async def get_articles(
    account_id: Optional[int] = None,
    category: Optional[str] = None,
    is_favorite: Optional[bool] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get articles with filters."""
    query = db.query(Article)
    
    if account_id:
        query = query.filter(Article.account_id == account_id)
    if category:
        query = query.filter(Article.category == category)
    if is_favorite is not None:
        query = query.filter(Article.is_favorite == is_favorite)
    
    total = query.count()
    articles = query.order_by(Article.published_at.desc()).offset(skip).limit(limit).all()
    
    return {"total": total, "items": articles}


@router.get("/{article_id}", response_model=schemas.ArticleDetail)
async def get_article(article_id: int, db: Session = Depends(get_db)):
    """Get article by ID with analysis."""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.post("/", response_model=schemas.Article)
async def create_article(
    article: schemas.ArticleCreate,
    db: Session = Depends(get_db)
):
    """Create new article."""
    db_article = Article(**article.model_dump())
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article


@router.put("/{article_id}", response_model=schemas.Article)
async def update_article(
    article_id: int,
    article_update: schemas.ArticleUpdate,
    db: Session = Depends(get_db)
):
    """Update article."""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    for key, value in article_update.model_dump(exclude_unset=True).items():
        setattr(article, key, value)
    
    db.commit()
    db.refresh(article)
    return article


@router.delete("/{article_id}")
async def delete_article(article_id: int, db: Session = Depends(get_db)):
    """Delete article."""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    db.delete(article)
    db.commit()
    return {"message": "Article deleted successfully"}


@router.post("/{article_id}/favorite", response_model=schemas.Article)
async def toggle_favorite(article_id: int, db: Session = Depends(get_db)):
    """Toggle article favorite status."""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    article.is_favorite = not article.is_favorite
    db.commit()
    db.refresh(article)
    return article


@router.post("/{article_id}/analyze")
async def analyze_article(article_id: int, db: Session = Depends(get_db)):
    """Analyze article with AI."""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Check if analysis already exists
    existing_analysis = db.query(ArticleAnalysis).filter(
        ArticleAnalysis.article_id == article_id
    ).first()
    
    if existing_analysis:
        return {"message": "Analysis already exists", "analysis_id": existing_analysis.id}
    
    # Perform AI analysis
    ai_service = AIService()
    analysis_result = await ai_service.analyze_article(
        article.title,
        article.content_text or article.content or ""
    )
    
    # Save analysis
    db_analysis = ArticleAnalysis(
        article_id=article_id,
        summary=analysis_result.get("summary"),
        keywords=analysis_result.get("keywords"),
        entities=analysis_result.get("entities"),
        category_confidence=analysis_result.get("category_confidence"),
        paper_info=analysis_result.get("paper_info"),
        tool_info=analysis_result.get("tool_info"),
        news_info=analysis_result.get("news_info"),
    )
    
    # Update article category
    article.category = analysis_result.get("category", "other")
    
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    
    return {"message": "Analysis completed", "analysis_id": db_analysis.id}


@router.get("/search/", response_model=schemas.ArticleList)
async def search_articles(
    q: str = Query(..., min_length=1),
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Search articles by title or content."""
    query = db.query(Article).filter(
        (Article.title.ilike(f"%{q}%")) | (Article.content_text.ilike(f"%{q}%"))
    )
    
    total = query.count()
    articles = query.order_by(Article.published_at.desc()).offset(skip).limit(limit).all()
    
    return {"total": total, "items": articles}


@router.post("/scrape", response_model=schemas.Article)
async def scrape_wechat_article(
    request: ScrapeArticleRequest,
    db: Session = Depends(get_db)
):
    """
    Scrape and save WeChat article from URL.
    
    - **url**: WeChat article URL (mp.weixin.qq.com)
    - **account_id**: Optional account ID to associate with
    - **auto_analyze**: Whether to automatically analyze with AI (default: True)
    """
    try:
        # Scrape article
        scraper = WeChatScraper()
        article_data = scraper.scrape_article(request.url)
        
        if not article_data:
            raise HTTPException(status_code=400, detail="Failed to scrape article: No data returned")
        
        # Check if article already exists
        existing = db.query(Article).filter(Article.url == request.url).first()
        if existing:
            raise HTTPException(status_code=400, detail="Article already exists")
        
        # Get or create account
        account_id = request.account_id
        if not account_id and article_data.get('account_name'):
            # Try to find existing account by name
            account = db.query(Account).filter(
                Account.name == article_data['account_name']
            ).first()
            
            if not account:
                # Create new account
                account = Account(
                    name=article_data['account_name'],
                    account_id=article_data['account_name'].lower().replace(' ', '_'),
                    description=f"Auto-created from article"
                )
                db.add(account)
                db.commit()
                db.refresh(account)
            
            account_id = account.id
        
        # Create article
        db_article = Article(
            account_id=account_id,
            title=article_data['title'],
            content=article_data['content'],
            content_text=article_data['content_text'],
            url=article_data['url'],
            author=article_data.get('author'),
            cover_image=article_data.get('cover_image'),
            published_at=article_data.get('published_at'),
        )
        
        db.add(db_article)
        db.commit()
        db.refresh(db_article)
        
        # Auto analyze if requested
        if request.auto_analyze:
            try:
                ai_service = AIService()
                analysis_result = await ai_service.analyze_article(
                    db_article.title,
                    db_article.content_text or ""
                )
                
                # Save analysis
                db_analysis = ArticleAnalysis(
                    article_id=db_article.id,
                    summary=analysis_result.get("summary"),
                    keywords=analysis_result.get("keywords"),
                    entities=analysis_result.get("entities"),
                    category_confidence=analysis_result.get("category_confidence"),
                    paper_info=analysis_result.get("paper_info"),
                    tool_info=analysis_result.get("tool_info"),
                    news_info=analysis_result.get("news_info"),
                )
                
                # Update article category
                db_article.category = analysis_result.get("category", "other")
                
                db.add(db_analysis)
                db.commit()
            except Exception as e:
                print(f"Auto-analysis failed: {str(e)}")
                # Continue even if analysis fails
        
        db.refresh(db_article)
        return db_article
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Scrape endpoint error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to scrape article: {str(e)}"
        )
