"""
富途OpenD客户端封装

提供连接管理、行情订阅、交易接口
"""
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
import futu as ft
from loguru import logger

from app.config import settings


class FutuClient:
    """富途OpenD客户端"""
    
    def __init__(self):
        self._quote_ctx: Optional[ft.OpenQuoteContext] = None
        self._trade_ctx: Optional[ft.OpenHKTradeContext] = None
        self._is_connected: bool = False
        self._host: str = settings.FUTU_HOST
        self._port: int = settings.FUTU_PORT
    
    @property
    def is_connected(self) -> bool:
        return self._is_connected
    
    def connect(self) -> bool:
        """连接OpenD"""
        try:
            # 创建行情上下文
            self._quote_ctx = ft.OpenQuoteContext(host=self._host, port=self._port)
            
            # 创建交易上下文（需要开通交易权限）
            # self._trade_ctx = ft.OpenHKTradeContext(host=self._host, port=self._port)
            
            # 测试连接
            ret, data = self._quote_ctx.get_global_state()
            if ret == ft.RET_OK:
                self._is_connected = True
                logger.info(f"OpenD连接成功: {self._host}:{self._port}")
                return True
            else:
                logger.error(f"OpenD连接失败: {data}")
                return False
                
        except Exception as e:
            logger.error(f"OpenD连接异常: {e}")
            self._is_connected = False
            return False
    
    def close(self):
        """关闭连接"""
        if self._quote_ctx:
            self._quote_ctx.close()
        if self._trade_ctx:
            self._trade_ctx.close()
        self._is_connected = False
        logger.info("OpenD连接已关闭")
    
    # ==================== 行情接口 ====================
    
    async def get_quote(self, stock_code: str) -> Dict[str, Any]:
        """获取实时行情"""
        if not self._is_connected or not self._quote_ctx:
            raise Exception("OpenD未连接")
        
        # 在线程池中执行同步调用
        loop = asyncio.get_event_loop()
        ret, data = await loop.run_in_executor(
            None, 
            lambda: self._quote_ctx.get_market_snapshot([stock_code])
        )
        
        if ret != ft.RET_OK:
            raise Exception(f"获取行情失败: {data}")
        
        row = data.iloc[0]
        return {
            "stock_code": row["code"],
            "stock_name": row["stock_name"],
            "current_price": float(row["last_price"]),
            "open_price": float(row["open_price"]),
            "high_price": float(row["high_price"]),
            "low_price": float(row["low_price"]),
            "prev_close_price": float(row["prev_close_price"]),
            "volume": int(row["volume"]),
            "turnover": float(row["turnover"]),
            "change": float(row["change_val"]),
            "change_ratio": float(row["change_rate"]),
            "updated_at": datetime.now()
        }
    
    async def get_kline(
        self, 
        stock_code: str, 
        start_date: str = None, 
        end_date: str = None,
        kline_type: str = "K_DAY"
    ) -> List[Dict[str, Any]]:
        """获取K线数据"""
        if not self._is_connected or not self._quote_ctx:
            raise Exception("OpenD未连接")
        
        # 映射K线类型
        ktype_map = {
            "K_DAY": ft.KLType.K_DAY,
            "K_WEEK": ft.KLType.K_WEEK,
            "K_MON": ft.KLType.K_MON,
            "K_1M": ft.KLType.K_1M,
            "K_5M": ft.KLType.K_5M,
            "K_15M": ft.KLType.K_15M,
            "K_30M": ft.KLType.K_30M,
            "K_60M": ft.KLType.K_60M,
        }
        
        loop = asyncio.get_event_loop()
        ret, data = await loop.run_in_executor(
            None,
            lambda: self._quote_ctx.get_cur_kline(
                code=stock_code,
                num=100,
                ktype=ktype_map.get(kline_type, ft.KLType.K_DAY)
            )
        )
        
        if ret != ft.RET_OK:
            raise Exception(f"获取K线数据失败: {data}")
        
        klines = []
        for _, row in data.iterrows():
            klines.append({
                "timestamp": datetime.fromtimestamp(row["time_key"]),
                "open_price": float(row["open"]),
                "high_price": float(row["high"]),
                "low_price": float(row["low"]),
                "close_price": float(row["close"]),
                "volume": int(row["volume"]),
                "turnover": float(row["turnover"])
            })
        
        return klines
    
    async def search_stock(self, keyword: str) -> List[Dict[str, Any]]:
        """搜索股票"""
        if not self._is_connected or not self._quote_ctx:
            raise Exception("OpenD未连接")
        
        loop = asyncio.get_event_loop()
        ret, data = await loop.run_in_executor(
            None,
            lambda: self._quote_ctx.get_stock_basicinfo(market=ft.Market.HK)
        )
        
        if ret != ft.RET_OK:
            raise Exception(f"搜索股票失败: {data}")
        
        # 过滤匹配结果
        keyword_lower = keyword.lower()
        results = []
        for _, row in data.iterrows():
            if (keyword_lower in row["code"].lower() or 
                keyword_lower in row["name"].lower()):
                results.append({
                    "stock_code": row["code"],
                    "stock_name": row["name"],
                    "market": row["market"]
                })
        
        return results[:20]  # 限制返回数量
    
    # ==================== 账户接口 ====================
    
    async def get_acc_info(self) -> Dict[str, Any]:
        """获取账户信息"""
        if not self._is_connected or not self._trade_ctx:
            raise Exception("OpenD未连接或交易权限未开通")
        
        loop = asyncio.get_event_loop()
        ret, data = await loop.run_in_executor(
            None,
            lambda: self._trade_ctx.accinfo_query()
        )
        
        if ret != ft.RET_OK:
            raise Exception(f"获取账户信息失败: {data}")
        
        row = data.iloc[0]
        return {
            "total_assets": float(row["total_assets"]),
            "cash": float(row["cash"]),
            "market_value": float(row["market_val"]),
            "frozen_cash": float(row["frozen_cash"]),
            "available_cash": float(row["avl_withdrawal_cash"]),
            "currency": "HKD",
            "updated_at": datetime.now()
        }
    
    async def get_positions(self) -> List[Dict[str, Any]]:
        """获取持仓列表"""
        if not self._is_connected or not self._trade_ctx:
            raise Exception("OpenD未连接或交易权限未开通")
        
        loop = asyncio.get_event_loop()
        ret, data = await loop.run_in_executor(
            None,
            lambda: self._trade_ctx.position_list_query()
        )
        
        if ret != ft.RET_OK:
            raise Exception(f"获取持仓列表失败: {data}")
        
        positions = []
        for _, row in data.iterrows():
            positions.append({
                "stock_code": row["code"],
                "stock_name": row["stock_name"],
                "quantity": int(row["qty"]),
                "available_quantity": int(row["can_sell_qty"]),
                "cost_price": float(row["cost_price"]),
                "current_price": float(row["market_val"] / row["qty"]) if row["qty"] > 0 else 0,
                "market_value": float(row["market_val"]),
                "profit_loss": float(row["pl_val"]),
                "profit_loss_ratio": float(row["pl_ratio"])
            })
        
        return positions
    
    # ==================== 交易接口 ====================
    
    async def place_order(
        self,
        stock_code: str,
        side: str,
        price: float,
        quantity: int,
        order_type: str = "LIMIT"
    ) -> Dict[str, Any]:
        """下单"""
        if not self._is_connected or not self._trade_ctx:
            raise Exception("OpenD未连接或交易权限未开通")
        
        # 映射买卖方向
        trd_side = ft.TrdSide.BUY if side == "BUY" else ft.TrdSide.SELL
        
        # 映射订单类型
        order_type_map = {
            "NORMAL": ft.OrderType.NORMAL,
            "MARKET": ft.OrderType.MARKET,
            "LIMIT": ft.OrderType.NORMAL,
            "STOP": ft.OrderType.STOP,
        }
        
        loop = asyncio.get_event_loop()
        ret, data = await loop.run_in_executor(
            None,
            lambda: self._trade_ctx.place_order(
                price=price,
                qty=quantity,
                code=stock_code,
                trd_side=trd_side,
                order_type=order_type_map.get(order_type, ft.OrderType.NORMAL)
            )
        )
        
        if ret != ft.RET_OK:
            raise Exception(f"下单失败: {data}")
        
        row = data.iloc[0]
        return {
            "order_id": row["order_id"],
            "stock_code": stock_code,
            "stock_name": "",  # 需要额外查询
            "side": side,
            "order_type": order_type,
            "price": price,
            "quantity": quantity,
            "filled_quantity": 0,
            "status": "SUBMITTED",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    
    async def cancel_order(self, order_id: str):
        """撤单"""
        if not self._is_connected or not self._trade_ctx:
            raise Exception("OpenD未连接或交易权限未开通")
        
        loop = asyncio.get_event_loop()
        ret, data = await loop.run_in_executor(
            None,
            lambda: self._trade_ctx.modify_order(
                modify_order_op=ft.ModifyOrderOp.CANCEL,
                order_id=order_id,
                quantity=0,
                price=0
            )
        )
        
        if ret != ft.RET_OK:
            raise Exception(f"撤单失败: {data}")
    
    async def get_orders(self, status: str = None) -> List[Dict[str, Any]]:
        """获取订单列表"""
        if not self._is_connected or not self._trade_ctx:
            raise Exception("OpenD未连接或交易权限未开通")
        
        loop = asyncio.get_event_loop()
        ret, data = await loop.run_in_executor(
            None,
            lambda: self._trade_ctx.order_list_query()
        )
        
        if ret != ft.RET_OK:
            raise Exception(f"获取订单列表失败: {data}")
        
        orders = []
        for _, row in data.iterrows():
            orders.append({
                "order_id": row["order_id"],
                "stock_code": row["code"],
                "stock_name": row["stock_name"],
                "side": "BUY" if row["trd_side"] == "BUY" else "SELL",
                "order_type": row["order_type"],
                "price": float(row["price"]),
                "quantity": int(row["qty"]),
                "filled_quantity": int(row["dealt_qty"]),
                "status": row["order_status"],
                "created_at": datetime.fromtimestamp(row["create_time"]),
                "updated_at": datetime.fromtimestamp(row["updated_time"])
            })
        
        return orders


# 全局客户端实例
futu_client = FutuClient()
