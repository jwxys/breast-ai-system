import logging
import time
from fastapi import Request

from app.core.config import settings


class LoggingMiddleware:
    """日志中间件"""
    
    def __init__(self, app):
        self.app = app
        self.logger = logging.getLogger(__name__)
        
        # 配置日志
        logging.basicConfig(
            level=getattr(logging, settings.LOG_LEVEL),
            format=settings.LOG_FORMAT
        )
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        
        request = Request(scope, receive=receive)
        
        # 记录请求
        start_time = time.time()
        self.logger.info(
            f"REQUEST [{request.method}] {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        # 执行请求
        try:
            response = await self.app(scope, receive, send)
            
            # 记录响应时间
            process_time = time.time() - start_time
            self.logger.info(
                f"RESPONSE [{request.method}] {request.url.path} "
                f"status={response.status if hasattr(response, 'status') else 200} "
                f"time={process_time:.3f}s"
            )
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            self.logger.error(
                f"ERROR [{request.method}] {request.url.path} "
                f"time={process_time:.3f}s error={str(e)}",
                exc_info=True
            )
            raise
