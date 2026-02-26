"""
交易服务API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

from app.services.futu_client import futu_client

router = APIRouter()


class OrderSide(str, Enum):
    """买卖方向"""
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    """订单类型"""
    NORMAL = "NORMAL"  # 普通订单
    MARKET = "MARKET"  # 市价单
    LIMIT = "LIMIT"    # 限价单
    STOP = "STOP"      # 止损单


class OrderStatus(str, Enum):
    """订单状态"""
    PENDING = "PENDING"        # 待提交
    SUBMITTED = "SUBMITTED"    # 已提交
    FILLED = "FILLED"          # 已成交
    CANCELLED = "CANCELLED"    # 已撤单
    REJECTED = "REJECTED"      # 已拒绝


class Order(BaseModel):
    """订单模型"""
    order_id: str
    stock_code: str
    stock_name: str
    side: OrderSide
    order_type: OrderType
    price: float
    quantity: int
    filled_quantity: int
    status: OrderStatus
    created_at: datetime
    updated_at: datetime


class OrderCreate(BaseModel):
    """创建订单请求"""
    stock_code: str
    side: OrderSide
    order_type: OrderType = OrderType.LIMIT
    price: float
    quantity: int
    acc_id: Optional[str] = None  # 账户ID
    stop_price: Optional[float] = None  # 止损价格
    take_profit_price: Optional[float] = None  # 止盈价格


class OrderCancel(BaseModel):
    """撤单请求"""
    order_id: str


@router.post("/order", response_model=Order, summary="下单")
async def create_order(order: OrderCreate):
    """
    创建交易订单

    - stock_code: 股票代码
    - side: 买卖方向 (BUY/SELL)
    - order_type: 订单类型
    - price: 价格
    - quantity: 数量
    - acc_id: 账户ID（可选，默认使用活跃账户）
    - stop_price: 止损价（可选）
    - take_profit_price: 止盈价（可选）
    """
    if not futu_client.is_connected or not futu_client.is_trade_enabled:
        raise HTTPException(status_code=400, detail="交易权限未开启")

    try:
        result = await futu_client.place_order(
            stock_code=order.stock_code,
            side=order.side.value,
            price=order.price,
            quantity=order.quantity,
            order_type=order.order_type.value,
            acc_id=order.acc_id
        )
        return Order(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下单失败: {str(e)}")


@router.delete("/order/{order_id}", summary="撤单")
async def cancel_order(order_id: str):
    """
    撤销指定订单
    
    - order_id: 订单ID
    """
    if not futu_client.is_connected:
        return {"message": f"订单 {order_id} 已撤销（模拟）", "success": True}
    
    try:
        await futu_client.cancel_order(order_id)
        return {"message": f"订单 {order_id} 已撤销", "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"撤单失败: {str(e)}")


@router.get("/orders", response_model=List[Order], summary="获取订单列表")
async def get_orders(status: Optional[OrderStatus] = None):
    """
    获取订单列表
    
    - status: 订单状态筛选（可选）
    """
    if not futu_client.is_connected:
        # 返回模拟数据（开发模式）
        return [
            Order(
                order_id="MOCK_001",
                stock_code="HK.00700",
                stock_name="腾讯控股",
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
                price=350.00,
                quantity=100,
                filled_quantity=100,
                status=OrderStatus.FILLED,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            Order(
                order_id="MOCK_002",
                stock_code="HK.09988",
                stock_name="阿里巴巴-SW",
                side=OrderSide.SELL,
                order_type=OrderType.LIMIT,
                price=80.00,
                quantity=200,
                filled_quantity=0,
                status=OrderStatus.SUBMITTED,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
    
    try:
        result = await futu_client.get_orders(status=status.value if status else None)
        return [Order(**o) for o in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取订单列表失败: {str(e)}")


@router.get("/order/{order_id}", response_model=Order, summary="获取订单详情")
async def get_order(order_id: str):
    """
    获取指定订单详情
    
    - order_id: 订单ID
    """
    if not futu_client.is_connected:
        raise HTTPException(status_code=404, detail=f"订单不存在: {order_id}")
    
    try:
        result = await futu_client.get_order(order_id)
        return Order(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取订单详情失败: {str(e)}")
