"""
应用配置管理
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用信息
    APP_NAME: str = "富途股票交易管理系统"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # 富途OpenD配置
    FUTU_HOST: str = "127.0.0.1"
    FUTU_PORT: int = 11111
    
    # 安全配置
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    
    # 数据库配置
    DATABASE_URL: str = "sqlite+aiosqlite:///./futu_trading.db"
    
    # 交易密码
    TRADE_PASSWORD: str = ""
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    
    # CORS配置
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"]
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            import json
            return json.loads(v)
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局配置实例
settings = Settings()
