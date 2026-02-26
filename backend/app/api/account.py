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
    acc_id: str
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
    trade_enabled: bool
    accounts: List[dict] = []
    last_sync: Optional[datetime]


class AccountListItem(BaseModel):
    """账户列表项"""
    acc_id: str
    trd_env: str
    acc_type: str
    acc_status: str
    uni_card_num: str = ""
    card_num: str = ""
    security_firm: str = ""
    trdmarket_auth: str = ""
    acc_role: str = ""


@router.get("/list", response_model=List[AccountListItem], summary="获取账户列表")
async def get_account_list():
    """
    获取所有可用账户列表
    """
    if not futu_client.is_connected or not futu_client.is_trade_enabled:
        return []

    return [
        AccountListItem(
            acc_id=acc["acc_id"],
            trd_env=acc["trd_env"],
            acc_type=acc["acc_type"],
            acc_status=acc["acc_status"],
            uni_card_num=acc.get("uni_card_num", ""),
            card_num=acc.get("card_num", ""),
            security_firm=acc.get("security_firm", ""),
            trdmarket_auth=acc.get("trdmarket_auth", ""),
            acc_role=acc.get("acc_role", ""),
        )
        for acc in futu_client.accounts
    ]


@router.get("/info", response_model=AccountInfo, summary="获取账户信息")
async def get_account_info(acc_id: str = None):
    """
    获取账户资金信息

    - acc_id: 账户ID（可选，默认使用活跃账户）
    - total_assets: 总资产
    - cash: 现金
    - market_value: 持仓市值
    - frozen_cash: 冻结资金
    - available_cash: 可用资金
    """
    # 未连接或交易权限未启用时返回模拟数据
    if not futu_client.is_connected or not futu_client.is_trade_enabled:
        return AccountInfo(
            acc_id="mock_account",
            total_assets=100000.00,
            cash=50000.00,
            market_value=50000.00,
            frozen_cash=0.00,
            available_cash=50000.00,
            currency="HKD",
            updated_at=datetime.now()
        )

    try:
        result = await futu_client.get_acc_info(acc_id)
        return AccountInfo(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取账户信息失败: {str(e)}")


@router.get("/positions", response_model=List[Position], summary="获取持仓列表")
async def get_positions():
    """
    获取当前持仓列表
    
    返回所有持仓股票的详细信息
    """
    # 未连接或交易权限未启用时返回模拟数据
    if not futu_client.is_connected or not futu_client.is_trade_enabled:
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

    - account_id: 当前活跃账户ID
    - status: 账户状态
    - opend_connected: OpenD连接状态
    - trade_enabled: 交易权限状态
    - accounts: 可用账户列表
    - last_sync: 最后同步时间
    """
    # 如果未连接，尝试重连
    if not futu_client.is_connected:
        futu_client.connect()

    return AccountStatus(
        account_id=futu_client.active_account_id or "未选择",
        status="active",
        opend_connected=futu_client.is_connected,
        trade_enabled=futu_client.is_trade_enabled,
        accounts=futu_client.accounts,
        last_sync=datetime.now() if futu_client.is_connected else None
    )


@router.post("/reconnect", summary="重新连接OpenD")
async def reconnect_opend():
    """
    手动重新连接OpenD

    当OpenD连接断开时，可调用此接口重新连接
    """
    # 先关闭现有连接
    futu_client.close()
    # 重新连接
    success = futu_client.connect()
    return {
        "success": success,
        "opend_connected": futu_client.is_connected,
        "trade_enabled": futu_client.is_trade_enabled,
        "active_account": futu_client.active_account_id,
        "accounts": futu_client.accounts,
        "message": "OpenD连接成功" if success else "OpenD连接失败"
    }
