"""
FastAPI应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.api import account, market, trade
from app.services.futu_client import futu_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print(f"[START] {settings.APP_NAME} v{settings.APP_VERSION} 启动中...")
    print(f"[INFO] 富途OpenD配置: {settings.FUTU_HOST}:{settings.FUTU_PORT}")

    # 尝试连接OpenD（如果可用）
    try:
        if futu_client.connect():
            print("[OK] OpenD连接成功")
        else:
            print("[WARN] OpenD未连接，部分功能不可用")
    except Exception as e:
        print(f"[WARN] OpenD连接失败: {e}")

    yield

    # 关闭时
    print("[INFO] 关闭OpenD连接...")
    futu_client.close()
    print("[OK] 应用已关闭")


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="富途股票交易管理系统API - 支持行情查询、交易下单、策略执行",
    lifespan=lifespan,
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(account.router, prefix="/api/account", tags=["账户管理"])
app.include_router(market.router, prefix="/api/market", tags=["行情服务"])
app.include_router(trade.router, prefix="/api/trade", tags=["交易服务"])


@app.get("/", tags=["根路径"])
async def root():
    """根路径 - API信息"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "opend_connected": futu_client.is_connected,
        "trade_enabled": futu_client.is_trade_enabled,
        "version": settings.APP_VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
