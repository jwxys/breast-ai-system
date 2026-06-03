"""
Knowledge Service

知识库管理服务
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import desc, func

from app.knowledge.models.knowledge_model import KnowledgeArticle, KnowledgeCategory


class KnowledgeService:
    """知识库服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_categories(self) -> List[KnowledgeCategory]:
        """获取所有分类"""
        return self.db.query(KnowledgeCategory).all()
    
    def get_category_by_id(self, category_id: int) -> Optional[KnowledgeCategory]:
        """根据 ID 获取分类"""
        return self.db.query(KnowledgeCategory).filter(
            KnowledgeCategory.id == category_id
        ).first()
    
    def create_category(self, name: str, code: str, description: str = "") -> KnowledgeCategory:
        """创建分类"""
        category = KnowledgeCategory(
            name=name,
            code=code,
            description=description
        )
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category
    
    def update_category(self, category_id: int, data: Dict[str, Any]) -> Optional[KnowledgeCategory]:
        """更新分类"""
        category = self.get_category_by_id(category_id)
        if not category:
            return None
        
        for key, value in data.items():
            if hasattr(category, key):
                setattr(category, key, value)
        
        self.db.commit()
        self.db.refresh(category)
        return category
    
    def get_articles(self, category_id: Optional[int] = None, 
                     status: Optional[str] = None,
                     skip: int = 0, limit: int = 20) -> List[KnowledgeArticle]:
        """获取文章列表"""
        query = self.db.query(KnowledgeArticle).options(
            selectinload(KnowledgeArticle.category)
        )
        
        if category_id:
            query = query.filter(KnowledgeArticle.category_id == category_id)
        if status:
            query = query.filter(KnowledgeArticle.status == status)
        
        return query.order_by(desc(KnowledgeArticle.created_at)).offset(skip).limit(limit).all()
    
    def get_article_by_id(self, article_id: int) -> Optional[KnowledgeArticle]:
        """根据 ID 获取文章"""
        return self.db.query(KnowledgeArticle).options(
            selectinload(KnowledgeArticle.category)
        ).filter(KnowledgeArticle.id == article_id).first()
    
    def search_articles(self, keyword: str, skip: int = 0, limit: int = 20) -> List[KnowledgeArticle]:
        """搜索文章"""
        return self.db.query(KnowledgeArticle).options(
            selectinload(KnowledgeArticle.category)
        ).filter(
            (KnowledgeArticle.title.ilike(f"%{keyword}%")) |
            (KnowledgeArticle.content.ilike(f"%{keyword}%")) |
            (KnowledgeArticle.keywords.ilike(f"%{keyword}%"))
        ).order_by(desc(KnowledgeArticle.created_at)).offset(skip).limit(limit).all()
    
    def create_article(self, data: Dict[str, Any]) -> KnowledgeArticle:
        """创建文章"""
        article = KnowledgeArticle(**data)
        self.db.add(article)
        self.db.commit()
        self.db.refresh(article)
        return article
    
    def update_article(self, article_id: int, data: Dict[str, Any]) -> Optional[KnowledgeArticle]:
        """更新文章"""
        article = self.get_article_by_id(article_id)
        if not article:
            return None
        
        for key, value in data.items():
            if hasattr(article, key):
                setattr(article, key, value)
        
        article.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(article)
        return article
    
    def publish_article(self, article_id: int) -> Optional[KnowledgeArticle]:
        """发布文章"""
        article = self.get_article_by_id(article_id)
        if not article:
            return None
        
        article.status = 'published'
        article.published_at = datetime.utcnow()
        article.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(article)
        return article
    
    def delete_article(self, article_id: int) -> bool:
        """删除文章"""
        article = self.get_article_by_id(article_id)
        if not article:
            return False
        
        self.db.delete(article)
        self.db.commit()
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        total_articles = self.db.query(func.count(KnowledgeArticle.id)).scalar()
        published_articles = self.db.query(func.count(KnowledgeArticle.id)).filter(
            KnowledgeArticle.status == 'published'
        ).scalar()
        total_categories = self.db.query(func.count(KnowledgeCategory.id)).scalar()
        
        # 按分类统计
        category_stats = self.db.query(
            KnowledgeCategory.name,
            func.count(KnowledgeArticle.id).label('article_count')
        ).join(
            KnowledgeArticle,
            KnowledgeCategory.id == KnowledgeArticle.category_id,
            isouter=True
        ).group_by(KnowledgeCategory.id).all()
        
        return {
            'total_articles': total_articles,
            'published_articles': published_articles,
            'draft_articles': total_articles - published_articles,
            'total_categories': total_categories,
            'by_category': [
                {'category': stat.name, 'count': stat.article_count}
                for stat in category_stats
            ]
        }
    
    def get_related_articles(self, article_id: int, limit: int = 5) -> List[KnowledgeArticle]:
        """获取相关文章"""
        article = self.get_article_by_id(article_id)
        if not article:
            return []
        
        # 根据分类和标签推荐
        return self.db.query(KnowledgeArticle).filter(
            KnowledgeArticle.id != article_id,
            KnowledgeArticle.category_id == article.category_id,
            KnowledgeArticle.status == 'published'
        ).order_by(desc(KnowledgeArticle.created_at)).limit(limit).all()
