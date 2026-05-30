import os
import shutil
import hashlib
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.models.data_management import ModelWeight
from app.core.config import settings


class WeightFileManager:
    """权重文件管理器"""
    
    # 权重存储目录
    WEIGHTS_DIR = Path(settings.ROOT_DIR) / "models"
    UPLOADS_DIR = Path(settings.ROOT_DIR) / "uploads" / "weights"
    
    # 支持的文件扩展名
    ALLOWED_EXTENSIONS = {".pth", ".pt", ".bin", ".onnx", ".json"}
    
    # 最大文件大小 (2GB)
    MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024
    
    @classmethod
    def ensure_directories(cls):
        """确保目录存在"""
        cls.WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
        cls.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate_file(cls, file: UploadFile) -> tuple[bool, str]:
        """
        验证上传文件
        
        Returns:
            (是否有效，错误信息)
        """
        # 检查文件扩展名
        file_ext = Path(file.filename).suffix.lower() if file.filename else ""
        if file_ext not in cls.ALLOWED_EXTENSIONS:
            return False, f"不支持的文件类型：{file_ext}，支持：{cls.ALLOWED_EXTENSIONS}"
        
        # 检查文件名
        if not file.filename or len(file.filename) > 255:
            return False, "文件名无效"
        
        return True, ""
    
    @classmethod
    async def calculate_file_hash(cls, file: UploadFile) -> str:
        """计算文件 SHA256 哈希"""
        file_hash = hashlib.sha256()
        
        # 读取文件内容计算哈希
        content = await file.read()
        file_hash.update(content)
        
        # 重置文件指针
        await file.seek(0)
        
        return file_hash.hexdigest()
    
    @classmethod
    async def upload_weight(
        cls,
        file: UploadFile,
        model_code: str,
        version: str,
        session: AsyncSession
    ) -> dict:
        """
        上传权重文件
        
        Args:
            file: 上传的文件
            model_code: 模型编码
            version: 版本号
            session: 数据库会话
        
        Returns:
            上传结果字典
        """
        # 确保目录存在
        cls.ensure_directories()
        
        # 验证文件
        is_valid, error_msg = cls.validate_file(file)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # 生成目标文件名
        file_ext = Path(file.filename).suffix.lower()
        safe_filename = f"{model_code}_{version}{file_ext}"
        target_path = cls.WEIGHTS_DIR / safe_filename
        
        # 检查是否已存在
        if target_path.exists():
            # 备份旧文件
            backup_path = cls.UPLOADS_DIR / f"{safe_filename}.backup.{datetime.now().strftime('%Y%m%d%H%M%S')}"
            shutil.copy2(target_path, backup_path)
        
        # 保存文件
        file_size = 0
        try:
            with open(target_path, 'wb') as buffer:
                while True:
                    chunk = await file.read(8192)
                    if not chunk:
                        break
                    buffer.write(chunk)
                    file_size += len(chunk)
            
            # 检查文件大小
            if file_size > cls.MAX_FILE_SIZE:
                target_path.unlink()
                raise HTTPException(status_code=400, detail="文件大小超过限制 (2GB)")
            
            # 计算文件哈希
            await file.seek(0)
            file_hash = await cls.calculate_file_hash(file)
            
        except Exception as e:
            if target_path.exists():
                target_path.unlink()
            raise HTTPException(status_code=500, detail=f"文件保存失败：{str(e)}")
        
        # 更新数据库记录
        relative_path = f"models/{safe_filename}"
        file_size_mb = round(file_size / (1024 * 1024), 2)
        
        # 查找或创建模型记录
        from sqlalchemy import select
        result = await session.execute(
            select(ModelWeight).where(ModelWeight.model_code == model_code)
        )
        weight = result.scalar_one_or_none()
        
        if weight:
            # 更新现有记录
            weight.weight_file = safe_filename
            weight.file_size_mb = file_size_mb
            weight.file_path = relative_path
            weight.version = version
            weight.updated_at = datetime.utcnow()
        else:
            # 创建新记录
            weight = ModelWeight(
                model_name=model_code,
                model_code=model_code,
                version=version,
                weight_file=safe_filename,
                file_size_mb=file_size_mb,
                file_path=relative_path,
                is_active=True,
                is_published=False
            )
            session.add(weight)
        
        await session.commit()
        await session.refresh(weight)
        
        return {
            "id": weight.id,
            "model_code": model_code,
            "version": version,
            "filename": safe_filename,
            "path": relative_path,
            "size_mb": file_size_mb,
            "sha256": file_hash,
            "upload_time": datetime.utcnow().isoformat()
        }
    
    @classmethod
    def get_weight_path(cls, model_code: str, version: Optional[str] = None) -> Optional[Path]:
        """
        获取权重文件路径
        
        Args:
            model_code: 模型编码
            version: 版本号 (可选)
        
        Returns:
            文件路径，不存在返回 None
        """
        if version:
            # 搜索特定版本
            for ext in cls.ALLOWED_EXTENSIONS:
                path = cls.WEIGHTS_DIR / f"{model_code}_{version}{ext}"
                if path.exists():
                    return path
        else:
            # 搜索最新版本
            for ext in cls.ALLOWED_EXTENSIONS:
                for file in cls.WEIGHTS_DIR.glob(f"{model_code}*{ext}"):
                    return file
        
        return None
    
    @classmethod
    def load_weight(cls, model_code: str, version: Optional[str] = None):
        """
        加载权重文件
        
        Args:
            model_code: 模型编码
            version: 版本号
        
        Returns:
            权重文件路径字符串
        """
        path = cls.get_weight_path(model_code, version)
        
        if not path:
            raise FileNotFoundError(f"权重文件不存在：{model_code}")
        
        return str(path)
    
    @classmethod
    async def delete_weight(cls, weight_id: int, session: AsyncSession) -> bool:
        """
        删除权重文件
        
        Args:
            weight_id: 权重记录 ID
            session: 数据库会话
        
        Returns:
            是否成功
        """
        from sqlalchemy import select
        
        result = await session.execute(
            select(ModelWeight).where(ModelWeight.id == weight_id)
        )
        weight = result.scalar_one_or_none()
        
        if not weight:
            return False
        
        # 删除文件
        if weight.file_path:
            file_path = Path(settings.ROOT_DIR) / weight.file_path
            if file_path.exists():
                # 移动到回收站
                backup_path = cls.UPLOADS_DIR / f"deleted_{weight.file_path.replace('/', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                shutil.move(str(file_path), str(backup_path))
        
        # 删除数据库记录
        await session.delete(weight)
        await session.commit()
        
        return True
    
    @classmethod
    def get_storage_stats(cls) -> dict:
        """获取存储统计"""
        cls.ensure_directories()
        
        total_size = 0
        file_count = 0
        
        for file in cls.WEIGHTS_DIR.glob("*"):
            if file.is_file():
                total_size += file.stat().st_size
                file_count += 1
        
        return {
            "total_files": file_count,
            "total_size_bytes": total_size,
            "total_size_gb": round(total_size / (1024 ** 3), 2),
            "weights_dir": str(cls.WEIGHTS_DIR),
            "uploads_dir": str(cls.UPLOADS_DIR)
        }


# 导出实例
weight_file_manager = WeightFileManager()
