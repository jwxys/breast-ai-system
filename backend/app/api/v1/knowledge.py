from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.knowledge import KnowledgeCategory, KnowledgeArticle, KnowledgeTag

router = APIRouter()


@router.get("/categories", summary="获取知识分类列表")
async def get_categories(session: AsyncSession = Depends(get_db)):
    """获取所有知识分类"""
    result = await session.execute(
        select(KnowledgeCategory)
        .where(KnowledgeCategory.is_deleted == False)
        .order_by(KnowledgeCategory.sort_order)
    )
    categories = result.scalars().all()
    
    return {
        "code": 200,
        "message": "success",
        "data": [
            {
                "id": cat.id,
                "name": cat.name,
                "code": cat.code,
                "icon": cat.icon,
                "description": cat.description,
                "article_count": cat.article_count or 0,
                "sort_order": cat.sort_order,
            }
            for cat in categories
        ]
    }


@router.get("/articles", summary="获取文章列表")
async def get_articles(
    category_id: Optional[int] = None,
    tag_id: Optional[int] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    session: AsyncSession = Depends(get_db)
):
    """获取知识文章列表"""
    query = select(KnowledgeArticle).options(
        selectinload(KnowledgeArticle.category),
        selectinload(KnowledgeArticle.tags)
    ).where(KnowledgeArticle.is_deleted == False)
    
    if category_id:
        query = query.where(KnowledgeArticle.category_id == category_id)
    if tag_id:
        query = query.where(KnowledgeArticle.tags.any(id=tag_id))
    if keyword:
        query = query.where(
            func.lower(KnowledgeArticle.title).like(f"%{keyword.lower()}%")
        )
    
    query = query.order_by(KnowledgeArticle.created_at.desc())
    
    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    result = await session.execute(query)
    articles = result.scalars().unique().all()
    
    # 获取总数
    count_query = select(func.count(KnowledgeArticle.id)).where(KnowledgeArticle.is_deleted == False)
    if category_id:
        count_query = count_query.where(KnowledgeArticle.category_id == category_id)
    if keyword:
        count_query = count_query.where(
            func.lower(KnowledgeArticle.title).like(f"%{keyword.lower()}%")
        )
    
    total_result = await session.execute(count_query)
    total = total_result.scalar()
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "list": [
                {
                    "id": art.id,
                    "title": art.title,
                    "summary": art.summary,
                    "category_id": art.category_id,
                    "category_name": art.category.name if art.category else None,
                    "tags": [{"id": tag.id, "name": tag.name} for tag in art.tags],
                    "view_count": art.view_count,
                    "created_at": art.created_at.isoformat(),
                    "updated_at": art.updated_at.isoformat(),
                }
                for art in articles
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    }


@router.get("/articles/{article_id}", summary="获取文章详情")
async def get_article(
    article_id: int,
    session: AsyncSession = Depends(get_db)
):
    """获取文章详情"""
    result = await session.execute(
        select(KnowledgeArticle)
        .options(selectinload(KnowledgeArticle.category), selectinload(KnowledgeArticle.tags))
        .where(KnowledgeArticle.id == article_id)
        .where(KnowledgeArticle.is_deleted == False)
    )
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    # 增加阅读量
    article.view_count += 1
    await session.commit()
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": article.id,
            "title": article.title,
            "category_id": article.category_id,
            "category_name": article.category.name if article.category else None,
            "content": article.content,
            "summary": article.summary,
            "tags": [{"id": tag.id, "name": tag.name} for tag in article.tags],
            "view_count": article.view_count,
            "created_at": article.created_at.isoformat(),
            "updated_at": article.updated_at.isoformat(),
            "related_articles": [],
        }
    }


@router.get("/tags", summary="获取标签列表")
async def get_tags(session: AsyncSession = Depends(get_db)):
    """获取所有标签"""
    result = await session.execute(
        select(KnowledgeTag)
        .order_by(KnowledgeTag.name)
    )
    tags = result.scalars().all()
    
    return {
        "code": 200,
        "message": "success",
        "data": [
            {"id": tag.id, "name": tag.name, "article_count": tag.article_count or 0}
            for tag in tags
        ]
    }


@router.get("/search", summary="搜索知识")
async def search_knowledge(
    keyword: str,
    category_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
    session: AsyncSession = Depends(get_db)
):
    """搜索知识文章"""
    query = select(KnowledgeArticle).where(
        KnowledgeArticle.is_deleted == False,
        func.lower(KnowledgeArticle.title).like(f"%{keyword.lower()}%")
    )
    
    if category_id:
        query = query.where(KnowledgeArticle.category_id == category_id)
    
    query = query.order_by(KnowledgeArticle.created_at.desc())
    
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    result = await session.execute(query)
    articles = result.scalars().all()
    
    return {
        "code": 200,
        "message": "success",
        "data": [
            {
                "id": art.id,
                "title": art.title,
                "summary": art.summary,
                "category_name": art.category.name if art.category else None,
                "created_at": art.created_at.isoformat(),
            }
            for art in articles
        ]
    }
