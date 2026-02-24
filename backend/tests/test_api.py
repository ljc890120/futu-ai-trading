"""
API测试
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


class TestHealthCheck:
    """健康检查测试"""
    
    def test_health_check(self):
        """测试健康检查接口"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestAccountAPI:
    """账户API测试"""
    
    def test_get_account_info(self):
        """测试获取账户信息"""
        response = client.get("/api/account/info")
        assert response.status_code == 200
        data = response.json()
        assert "total_assets" in data
        assert "cash" in data
        assert "market_value" in data
    
    def test_get_positions(self):
        """测试获取持仓列表"""
        response = client.get("/api/account/positions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_account_status(self):
        """测试获取账户状态"""
        response = client.get("/api/account/status")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "opend_connected" in data


class TestMarketAPI:
    """行情API测试"""
    
    def test_get_quote(self):
        """测试获取实时行情"""
        response = client.get("/api/market/quote/HK.00700")
        assert response.status_code == 200
        data = response.json()
        assert "stock_code" in data
        assert "current_price" in data
    
    def test_get_quote_not_found(self):
        """测试获取不存在的股票行情"""
        response = client.get("/api/market/quote/HK.99999")
        assert response.status_code == 404
    
    def test_get_kline(self):
        """测试获取K线数据"""
        response = client.get("/api/market/kline/HK.00700")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_search_stock(self):
        """测试搜索股票"""
        response = client.get("/api/market/search?keyword=腾讯")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestTradeAPI:
    """交易API测试"""
    
    def test_create_order(self):
        """测试创建订单"""
        order_data = {
            "stock_code": "HK.00700",
            "side": "BUY",
            "order_type": "LIMIT",
            "price": 350.00,
            "quantity": 100
        }
        response = client.post("/api/trade/order", json=order_data)
        assert response.status_code == 200
        data = response.json()
        assert "order_id" in data
        assert data["status"] == "SUBMITTED"
    
    def test_get_orders(self):
        """测试获取订单列表"""
        response = client.get("/api/trade/orders")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_cancel_order(self):
        """测试撤单"""
        response = client.delete("/api/trade/order/MOCK_002")
        assert response.status_code == 200
