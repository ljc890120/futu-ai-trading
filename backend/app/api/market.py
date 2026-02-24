"""
行情服务API
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import json

from app.services.futu_client import futu_client

router = APIRouter()


class Quote(BaseModel):
    """实时行情模型"""
    stock_code: str
    stock_name: str
    current_price: float
    open_price: float
    high_price: float
    low_price: float
    prev_close_price: float
    volume: int
    turnover: float
    change: float
    change_ratio: float
    updated_at: datetime


class KLine(BaseModel):
    """K线数据模型"""
    timestamp: datetime
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int
    turnover: float


class StockSearch(BaseModel):
    """股票搜索结果模型"""
    stock_code: str
    stock_name: str
    market: str


@router.get("/quote/{stock_code}", response_model=Quote, summary="获取实时行情")
async def get_quote(stock_code: str):
    """
    获取指定股票的实时行情
    
    - stock_code: 股票代码，如 HK.00700
    """
    if not futu_client.is_connected:
        # 返回模拟数据（开发模式）
        mock_data = {
            "HK.00700": ("腾讯控股", 360.00),
            "HK.09988": ("阿里巴巴-SW", 75.00),
            "HK.00941": ("中国移动", 70.00),
            "US.AAPL": ("Apple Inc.", 185.00),
        }
        
        if stock_code in mock_data:
            name, price = mock_data[stock_code]
            return Quote(
                stock_code=stock_code,
                stock_name=name,
                current_price=price,
                open_price=price * 0.99,
                high_price=price * 1.01,
                low_price=price * 0.98,
                prev_close_price=price * 0.995,
                volume=10000000,
                turnover=price * 10000000,
                change=price * 0.005,
                change_ratio=0.005,
                updated_at=datetime.now()
            )
        else:
            raise HTTPException(status_code=404, detail=f"未找到股票: {stock_code}")
    
    try:
        result = await futu_client.get_quote(stock_code)
        return Quote(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取行情失败: {str(e)}")


@router.get("/kline/{stock_code}", response_model=List[KLine], summary="获取K线数据")
async def get_kline(
    stock_code: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    kline_type: str = "K_DAY"
):
    """
    获取股票K线数据
    
    - stock_code: 股票代码
    - start_date: 开始日期 (YYYY-MM-DD)
    - end_date: 结束日期 (YYYY-MM-DD)
    - kline_type: K线类型 (K_DAY, K_WEEK, K_MON, K_1M, K_5M, K_15M, K_30M, K_60M)
    """
    if not futu_client.is_connected:
        # 返回模拟数据（开发模式）
        import random
        from datetime import timedelta
        
        base_price = 350.0
        klines = []
        for i in range(30):
            date = datetime.now() - timedelta(days=30-i)
            open_p = base_price * (1 + random.uniform(-0.02, 0.02))
            close_p = open_p * (1 + random.uniform(-0.03, 0.03))
            high_p = max(open_p, close_p) * (1 + random.uniform(0, 0.02))
            low_p = min(open_p, close_p) * (1 - random.uniform(0, 0.02))
            volume = random.randint(5000000, 15000000)
            
            klines.append(KLine(
                timestamp=date,
                open_price=round(open_p, 2),
                high_price=round(high_p, 2),
                low_price=round(low_p, 2),
                close_price=round(close_p, 2),
                volume=volume,
                turnover=round(close_p * volume, 2)
            ))
            base_price = close_p
        
        return klines
    
    try:
        result = await futu_client.get_kline(stock_code, start_date, end_date, kline_type)
        return [KLine(**k) for k in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取K线数据失败: {str(e)}")


@router.get("/search", response_model=List[StockSearch], summary="搜索股票")
async def search_stock(keyword: str):
    """
    根据关键词搜索股票
    
    - keyword: 股票代码或名称关键词
    """
    if not futu_client.is_connected:
        # 返回模拟搜索结果（开发模式）
        mock_stocks = [
            {"stock_code": "HK.00700", "stock_name": "腾讯控股", "market": "HK"},
            {"stock_code": "HK.09988", "stock_name": "阿里巴巴-SW", "market": "HK"},
            {"stock_code": "HK.00941", "stock_name": "中国移动", "market": "HK"},
            {"stock_code": "US.AAPL", "stock_name": "Apple Inc.", "market": "US"},
            {"stock_code": "US.TSLA", "stock_name": "Tesla Inc.", "market": "US"},
        ]
        
        keyword_lower = keyword.lower()
        results = [
            StockSearch(**s) for s in mock_stocks
            if keyword_lower in s["stock_code"].lower() or keyword_lower in s["stock_name"].lower()
        ]
        return results
    
    try:
        result = await futu_client.search_stock(keyword)
        return [StockSearch(**s) for s in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索股票失败: {str(e)}")


# WebSocket实时行情推送
@router.websocket("/ws/{stock_code}")
async def websocket_quote(websocket: WebSocket, stock_code: str):
    """
    WebSocket实时行情推送
    
    连接后会持续推送指定股票的实时行情
    """
    await websocket.accept()
    
    try:
        while True:
            # 获取行情数据
            quote = await get_quote(stock_code)
            
            # 发送数据
            await websocket.send_json(quote.model_dump())
            
            # 等待1秒
            import asyncio
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        print(f"WebSocket断开连接: {stock_code}")
    except Exception as e:
        print(f"WebSocket错误: {e}")
    finally:
        await websocket.close()
