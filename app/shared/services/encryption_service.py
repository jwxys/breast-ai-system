"""
数据加密服务

使用 Fernet 对称加密算法保护患者敏感数据
"""
import os
import base64
from typing import Optional
from cryptography.fernet import Fernet
from app.core.config import settings


class EncryptionService:
    """加密服务"""
    
    _instance: Optional['EncryptionService'] = None
    _cipher: Optional[Fernet] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化加密器"""
        if self._cipher is None:
            # 获取或生成加密密钥
            key = self._get_or_create_key()
            self._cipher = Fernet(key)
    
    def _get_or_create_key(self) -> bytes:
        """获取或创建加密密钥"""
        key_file = settings.ENCRYPTION_KEY_FILE
        
        if os.path.exists(key_file):
            # 读取已有密钥
            with open(key_file, 'rb') as f:
                key = f.read().strip()
        else:
            # 生成新密钥
            key = Fernet.generate_key()
            
            # 确保目录存在
            os.makedirs(os.path.dirname(key_file), exist_ok=True)
            
            # 保存密钥（权限设置为仅所有者可读写）
            with open(key_file, 'wb') as f:
                f.write(key)
            os.chmod(key_file, 0o600)
        
        return key
    
    def encrypt(self, data: str) -> str:
        """
        加密字符串
        
        Args:
            data: 待加密的明文
            
        Returns:
            Base64 编码的密文
        """
        if not data:
            return data
        
        encrypted = self._cipher.encrypt(data.encode('utf-8'))
        return base64.urlsafe_b64encode(encrypted).decode('utf-8')
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        解密密文
        
        Args:
            encrypted_data: Base64 编码的密文
            
        Returns:
            解密后的明文
        """
        if not encrypted_data:
            return encrypted_data
        
        try:
            encrypted = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
            decrypted = self._cipher.decrypt(encrypted)
            return decrypted.decode('utf-8')
        except Exception as e:
            # 记录日志但不抛出异常，避免暴露敏感信息
            print(f"Decryption failed: {e}")
            return ""
    
    def encrypt_field(self, value: Optional[str]) -> Optional[str]:
        """加密字段值（处理 None）"""
        if value is None:
            return None
        return self.encrypt(value)
    
    def decrypt_field(self, value: Optional[str]) -> Optional[str]:
        """解密字段值（处理 None）"""
        if value is None:
            return None
        return self.decrypt(value)


# 全局加密服务实例
encryption_service = EncryptionService()


def encrypt_patient_data(data: dict) -> dict:
    """
    加密患者敏感数据
    
    Args:
        data: 患者数据字典
        
    Returns:
        加密后的数据字典
    """
    sensitive_fields = ['name', 'id_number', 'phone', 'address', 'emergency_contact', 'emergency_phone']
    
    encrypted_data = data.copy()
    for field in sensitive_fields:
        if field in encrypted_data and encrypted_data[field]:
            encrypted_data[field] = encryption_service.encrypt(str(encrypted_data[field]))
    
    return encrypted_data


def decrypt_patient_data(data: dict) -> dict:
    """
    解密患者敏感数据
    
    Args:
        data: 加密的患者数据字典
        
    Returns:
        解密后的数据字典
    """
    sensitive_fields = ['name', 'id_number', 'phone', 'address', 'emergency_contact', 'emergency_phone']
    
    decrypted_data = data.copy()
    for field in sensitive_fields:
        if field in decrypted_data and decrypted_data[field]:
            decrypted_data[field] = encryption_service.decrypt(str(decrypted_data[field]))
    
    return decrypted_data
