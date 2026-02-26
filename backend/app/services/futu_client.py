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
        self._trade_ctx_us: Optional[ft.OpenUSTradeContext] = None
        self._is_connected: bool = False
        self._trade_enabled: bool = False
        self._accounts: List[Dict] = []
        self._active_account_id: Optional[str] = None
        self._host: str = settings.FUTU_HOST
        self._port: int = settings.FUTU_PORT

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    @property
    def is_trade_enabled(self) -> bool:
        return self._trade_enabled

    @property
    def accounts(self) -> List[Dict]:
        return self._accounts

    @property
    def active_account_id(self) -> Optional[str]:
        return self._active_account_id

    def connect(self) -> bool:
        """连接OpenD"""
        try:
            # 创建行情上下文
            self._quote_ctx = ft.OpenQuoteContext(host=self._host, port=self._port)

            # 测试行情连接
            ret, data = self._quote_ctx.get_global_state()
            if ret == ft.RET_OK:
                self._is_connected = True
                logger.info(f"OpenD行情连接成功: {self._host}:{self._port}")

                # 创建交易上下文
                try:
                    self._trade_ctx = ft.OpenHKTradeContext(host=self._host, port=self._port)
                    self._trade_ctx_us = ft.OpenUSTradeContext(host=self._host, port=self._port)
                    # 解锁交易（需要交易密码）
                    if settings.TRADE_PASSWORD:
                        unlock_ret, unlock_data = self._trade_ctx.unlock_trade(settings.TRADE_PASSWORD)
                        if unlock_ret == ft.RET_OK:
                            self._trade_enabled = True
                            logger.info("OpenD交易权限已解锁")
                            # 同步解锁美股上下文
                            self._trade_ctx_us.unlock_trade(settings.TRADE_PASSWORD)

                            # 从港股和美股上下文各获取账户列表，合并去重
                            acc_map: Dict[str, Dict] = {}
                            for ctx, market_label in [
                                (self._trade_ctx, "HK"),
                                (self._trade_ctx_us, "US"),
                            ]:
                                acc_ret, acc_data = ctx.get_acc_list()
                                if acc_ret == ft.RET_OK:
                                    for _, row in acc_data.iterrows():
                                        acc_id = str(row["acc_id"])
                                        if acc_id not in acc_map:
                                            acc_map[acc_id] = {
                                                "acc_id": acc_id,
                                                "trd_env": row["trd_env"],
                                                "acc_type": row["acc_type"],
                                                "acc_status": row["acc_status"],
                                                "uni_card_num": row.get("uni_card_num", ""),
                                                "card_num": row.get("card_num", ""),
                                                "security_firm": row.get("security_firm", ""),
                                                "trdmarket_auth": row.get("trdmarket_auth", ""),
                                                "acc_role": row.get("acc_role", ""),
                                            }
                                    logger.info(f"[{market_label}] 获取到 {len(acc_data)} 个账户")
                                else:
                                    logger.warning(f"[{market_label}] 获取账户列表失败: {acc_data}")

                            self._accounts = list(acc_map.values())
                            logger.info(f"合并去重后共 {len(self._accounts)} 个账户")
                            for acc in self._accounts:
                                logger.info(
                                    f"  acc_id={acc['acc_id']} trd_env={acc['trd_env']} "
                                    f"acc_status={acc['acc_status']} market={acc.get('trdmarket_auth', '')}"
                                )

                            # 优先选择活跃的真实账户，其次活跃模拟账户
                            for acc in self._accounts:
                                if acc["acc_status"] == "ACTIVE" and acc["trd_env"] == "REAL":
                                    self._active_account_id = acc["acc_id"]
                                    logger.info(f"默认选择真实账户: {acc['acc_id']}")
                                    break
                            if not self._active_account_id:
                                for acc in self._accounts:
                                    if acc["acc_status"] == "ACTIVE":
                                        self._active_account_id = acc["acc_id"]
                                        logger.info(f"默认选择账户: {acc['acc_id']} ({acc['trd_env']})")
                                        break
                        else:
                            logger.warning(f"交易解锁失败: {unlock_data}")
                    else:
                        logger.warning("未配置交易密码，交易功能不可用")
                except Exception as te:
                    logger.warning(f"交易上下文创建失败: {te}")

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
        if self._trade_ctx_us:
            self._trade_ctx_us.close()
        self._is_connected = False
        logger.info("OpenD连接已关闭")
    
    def _get_trade_ctx_for_account(self, acc_id: str):
        """根据账户的市场权限选择合适的交易上下文"""
        for acc in self._accounts:
            if acc["acc_id"] == acc_id:
                market_auth = acc.get("trdmarket_auth", "")
                # 如果账户有 US 市场权限且无 HK 权限，优先用美股上下文
                has_hk = "HK" in str(market_auth)
                has_us = "US" in str(market_auth)
                if has_us and not has_hk and self._trade_ctx_us:
                    return self._trade_ctx_us
                break
        return self._trade_ctx

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
        # 计算涨跌额和涨跌幅
        last_price = float(row["last_price"])
        prev_close = float(row["prev_close_price"]) if row["prev_close_price"] != "N/A" else last_price
        change = last_price - prev_close
        change_ratio = (change / prev_close * 100) if prev_close > 0 else 0

        return {
            "stock_code": row["code"],
            "stock_name": row["name"],
            "current_price": last_price,
            "open_price": float(row["open_price"]) if row["open_price"] != "N/A" else last_price,
            "high_price": float(row["high_price"]) if row["high_price"] != "N/A" else last_price,
            "low_price": float(row["low_price"]) if row["low_price"] != "N/A" else last_price,
            "prev_close_price": prev_close,
            "volume": int(row["volume"]) if row["volume"] != "N/A" else 0,
            "turnover": float(row["turnover"]) if row["turnover"] != "N/A" else 0,
            "change": change,
            "change_ratio": change_ratio,
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

    async def get_acc_info(self, acc_id: str = None) -> Dict[str, Any]:
        """获取账户信息"""
        if not self._is_connected or not self._trade_ctx:
            raise Exception("OpenD未连接或交易权限未开通")

        # 使用指定的账户ID或当前活跃账户
        target_acc_id = acc_id or self._active_account_id
        if not target_acc_id:
            raise Exception("未指定账户ID")

        # 查找账户环境
        trd_env = ft.TrdEnv.REAL
        for acc in self._accounts:
            if acc["acc_id"] == target_acc_id:
                trd_env = ft.TrdEnv.SIMULATE if acc["trd_env"] == "SIMULATE" else ft.TrdEnv.REAL
                break

        trade_ctx = self._get_trade_ctx_for_account(target_acc_id)
        loop = asyncio.get_event_loop()
        ret, data = await loop.run_in_executor(
            None,
            lambda: trade_ctx.accinfo_query(acc_id=int(target_acc_id), trd_env=trd_env)
        )

        if ret != ft.RET_OK:
            raise Exception(f"获取账户信息失败: {data}")

        row = data.iloc[0]
        return {
            "acc_id": target_acc_id,
            "total_assets": float(row["total_assets"]) if row["total_assets"] != "N/A" else 0.0,
            "cash": float(row["cash"]) if row["cash"] != "N/A" else 0.0,
            "market_value": float(row["market_val"]) if row["market_val"] != "N/A" else 0.0,
            "frozen_cash": float(row["frozen_cash"]) if row["frozen_cash"] != "N/A" else 0.0,
            "available_cash": float(row["avl_withdrawal_cash"]) if row["avl_withdrawal_cash"] != "N/A" else 0.0,
            "currency": "HKD",
            "updated_at": datetime.now()
        }

    async def get_positions(self, acc_id: str = None) -> List[Dict[str, Any]]:
        """获取持仓列表"""
        if not self._is_connected or not self._trade_ctx:
            raise Exception("OpenD未连接或交易权限未开通")

        # 使用指定的账户ID或当前活跃账户
        target_acc_id = acc_id or self._active_account_id
        if not target_acc_id:
            raise Exception("未指定账户ID")

        # 查找账户环境
        trd_env = ft.TrdEnv.REAL
        for acc in self._accounts:
            if acc["acc_id"] == target_acc_id:
                trd_env = ft.TrdEnv.SIMULATE if acc["trd_env"] == "SIMULATE" else ft.TrdEnv.REAL
                break

        trade_ctx = self._get_trade_ctx_for_account(target_acc_id)
        loop = asyncio.get_event_loop()
        ret, data = await loop.run_in_executor(
            None,
            lambda: trade_ctx.position_list_query(acc_id=int(target_acc_id), trd_env=trd_env)
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
        order_type: str = "LIMIT",
        acc_id: str = None
    ) -> Dict[str, Any]:
        """下单"""
        if not self._is_connected or not self._trade_ctx:
            raise Exception("OpenD未连接或交易权限未开通")

        # 使用指定的账户ID或当前活跃账户
        target_acc_id = acc_id or self._active_account_id
        if not target_acc_id:
            raise Exception("未指定账户ID")

        # 查找账户环境
        trd_env = ft.TrdEnv.REAL
        for acc in self._accounts:
            if acc["acc_id"] == target_acc_id:
                trd_env = ft.TrdEnv.SIMULATE if acc["trd_env"] == "SIMULATE" else ft.TrdEnv.REAL
                break

        # 映射买卖方向
        trd_side = ft.TrdSide.BUY if side == "BUY" else ft.TrdSide.SELL

        # 映射订单类型
        order_type_map = {
            "NORMAL": ft.OrderType.NORMAL,
            "MARKET": ft.OrderType.MARKET,
            "LIMIT": ft.OrderType.NORMAL,
            "STOP": ft.OrderType.STOP,
        }

        trade_ctx = self._get_trade_ctx_for_account(target_acc_id)
        loop = asyncio.get_event_loop()
        ret, data = await loop.run_in_executor(
            None,
            lambda: trade_ctx.place_order(
                price=price,
                qty=quantity,
                code=stock_code,
                trd_side=trd_side,
                order_type=order_type_map.get(order_type, ft.OrderType.NORMAL),
                acc_id=int(target_acc_id),
                trd_env=trd_env
            )
        )

        if ret != ft.RET_OK:
            raise Exception(f"下单失败: {data}")

        row = data.iloc[0]
        return {
            "order_id": row["order_id"],
            "stock_code": stock_code,
            "stock_name": row.get("stock_name", ""),
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
