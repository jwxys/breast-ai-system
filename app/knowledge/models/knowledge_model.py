from sqlalchemy import Column, BigInteger, String, Text, Integer, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


# 知识和标签关联表
knowledge_article_tags = Table(
    'knowledge_article_tags',
    Base.metadata,
    Column('article_id', BigInteger, ForeignKey('knowledge_article.id'), primary_key=True),
    Column('tag_id', BigInteger, ForeignKey('knowledge_tag.id'), primary_key=True)
)


class KnowledgeCategory(Base):
    """知识分类表"""
    __tablename__ = 'knowledge_category'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False, comment='分类名称')
    code = Column(String(64), unique=True, nullable=False, comment='分类编码')
    description = Column(Text, comment='分类描述')
    icon = Column(String(64), comment='图标')
    parent_id = Column(BigInteger, ForeignKey('knowledge_category.id'), comment='父分类 ID')
    sort_order = Column(Integer, default=0, comment='排序顺序')
    article_count = Column(Integer, default=0, comment='文章数量')
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    articles = relationship("KnowledgeArticle", back_populates="category")
    parent = relationship("KnowledgeCategory", remote_side=[id], backref="children")


class KnowledgeTag(Base):
    """知识标签表"""
    __tablename__ = 'knowledge_tag'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(64), unique=True, nullable=False, comment='标签名称')
    color = Column(String(16), default='#667eea', comment='标签颜色')
    article_count = Column(Integer, default=0, comment='文章数量')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联
    articles = relationship("KnowledgeArticle", secondary=knowledge_article_tags, back_populates="tags")


class KnowledgeArticle(Base):
    """知识文章表"""
    __tablename__ = 'knowledge_article'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String(256), nullable=False, comment='文章标题')
    content = Column(Text, nullable=False, comment='文章内容 (Markdown)')
    summary = Column(String(512), comment='文章摘要')
    category_id = Column(BigInteger, ForeignKey('knowledge_category.id'), comment='分类 ID')
    cover_image = Column(String(512), comment='封面图片 URL')
    author = Column(String(128), comment='作者')
    view_count = Column(Integer, default=0, comment='阅读量')
    like_count = Column(Integer, default=0, comment='点赞数')
    is_published = Column(Boolean, default=False, comment='是否发布')
    is_deleted = Column(Boolean, default=False)
    published_at = Column(DateTime, comment='发布时间')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    category = relationship("KnowledgeCategory", back_populates="articles")
    tags = relationship("KnowledgeTag", secondary=knowledge_article_tags, back_populates="articles")
