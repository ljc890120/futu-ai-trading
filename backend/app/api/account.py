"""
账户管理API
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.services.futu_client import futu_client

router = APIRouter()


class AccountInfo(BaseModel):
    """账户信息模型"""
    total_assets: float
    cash: float
    market_value: float
    frozen_cash: float
    available_cash: float
    currency: str
    updated_at: datetime


class Position(BaseModel):
    """持仓模型"""
    stock_code: str
    stock_name: str
    quantity: int
    available_quantity: int
    cost_price: float
    current_price: float
    market_value: float
    profit_loss: float
    profit_loss_ratio: float


class AccountStatus(BaseModel):
    """账户状态模型"""
    account_id: str
    status: str
    opend_connected: bool
    last_sync: Optional[datetime]


@router.get("/info", response_model=AccountInfo, summary="获取账户信息")
async def get_account_info():
    """
    获取账户资金信息
    
    - total_assets: 总资产
    - cash: 现金
    - market_value: 持仓市值
    - frozen_cash: 冻结资金
    - available_cash: 可用资金
    """
    if not futu_client.is_connected:
        # 返回模拟数据（开发模式）
        return AccountInfo(
            total_assets=100000.00,
            cash=50000.00,
            market_value=50000.00,
            frozen_cash=0.00,
            available_cash=50000.00,
            currency="HKD",
            updated_at=datetime.now()
        )
    
    try:
        result = await futu_client.get_acc_info()
        return AccountInfo(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取账户信息失败: {str(e)}")


@router.get("/positions", response_model=List[Position], summary="获取持仓列表")
async def get_positions():
    """
    获取当前持仓列表
    
    返回所有持仓股票的详细信息
    """
    if not futu_client.is_connected:
        # 返回模拟数据（开发模式）
        return [
            Position(
                stock_code="HK.00700",
                stock_name="腾讯控股",
                quantity=100,
                available_quantity=100,
                cost_price=350.00,
                current_price=360.00,
                market_value=36000.00,
                profit_loss=1000.00,
                profit_loss_ratio=0.0286
            ),
            Position(
                stock_code="HK.09988",
                stock_name="阿里巴巴-SW",
                quantity=200,
                available_quantity=200,
                cost_price=80.00,
                current_price=75.00,
                market_value=15000.00,
                profit_loss=-1000.00,
                profit_loss_ratio=-0.0625
            )
        ]
    
    try:
        result = await futu_client.get_positions()
        return [Position(**p) for p in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取持仓列表失败: {str(e)}")


@router.get("/status", response_model=AccountStatus, summary="获取账户状态")
async def get_account_status():
    """
    获取账户连接状态
    
    - account_id: 账户ID
    - status: 账户状态
    - opend_connected: OpenD连接状态
    - last_sync: 最后同步时间
    """
    return AccountStatus(
        account_id="dev_account",
        status="active",
        opend_connected=futu_client.is_connected,
        last_sync=datetime.now() if futu_client.is_connected else None
    )
