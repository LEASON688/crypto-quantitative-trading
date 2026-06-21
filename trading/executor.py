"""
交易执行引擎
负责下单、订单管理和交易执行
"""

import logging
from typing import Dict, Optional, List
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class OrderType(Enum):
    """订单类型"""
    LIMIT = "limit"
    MARKET = "market"


class OrderSide(Enum):
    """订单方向"""
    BUY = "buy"
    SELL = "sell"


class TradeExecutor:
    """交易执行器"""

    def __init__(self, exchange_api, config: Dict):
        """
        初始化交易执行器
        
        Args:
            exchange_api: 交易所 API 接口
            config: 配置字典
        """
        self.exchange_api = exchange_api
        self.config = config
        self.trading_enabled = config.get("TRADING_ENABLED", False)
        self.paper_trading = config.get("PAPER_TRADING", True)
        self.open_orders = {}  # 跟踪未成交订单
        self.closed_orders = []  # 已成交订单历史

    def execute_buy_order(
        self,
        exchange: str,
        symbol: str,
        amount: float,
        price: Optional[float] = None,
        order_type: str = "limit",
    ) -> Optional[Dict]:
        """
        执行买入订单
        
        Args:
            exchange: 交易所名称
            symbol: 交易对
            amount: 购买数量
            price: 价格 (limit 订单需要)
            order_type: 订单类型
            
        Returns:
            订单信息
        """
        if not self.trading_enabled and not self.paper_trading:
            logger.warning("交易未启用")
            return None

        try:
            if self.paper_trading:
                # 纸面交易 (模拟)
                order = self._simulate_order(
                    exchange, symbol, "buy", amount, price
                )
                logger.info(f"✓ 模拟买入订单: {symbol} {amount} @ {price}")
            else:
                # 真实交易
                order = self.exchange_api.create_order(
                    exchange, symbol, order_type, "buy", amount, price
                )
                logger.info(f"✓ 真实买入订单已下单: {symbol}")
            
            if order:
                self.open_orders[order["id"]] = order
            
            return order
        except Exception as e:
            logger.error(f"买入订单执行失败: {e}")
            return None

    def execute_sell_order(
        self,
        exchange: str,
        symbol: str,
        amount: float,
        price: Optional[float] = None,
        order_type: str = "limit",
    ) -> Optional[Dict]:
        """
        执行卖出订单
        
        Args:
            exchange: 交易所名称
            symbol: 交易对
            amount: 卖出数量
            price: 价格 (limit 订单需要)
            order_type: 订单类型
            
        Returns:
            订单信息
        """
        if not self.trading_enabled and not self.paper_trading:
            logger.warning("交易未启用")
            return None

        try:
            if self.paper_trading:
                # 纸面交易
                order = self._simulate_order(
                    exchange, symbol, "sell", amount, price
                )
                logger.info(f"✓ 模拟卖出订单: {symbol} {amount} @ {price}")
            else:
                # 真实交易
                order = self.exchange_api.create_order(
                    exchange, symbol, order_type, "sell", amount, price
                )
                logger.info(f"✓ 真实卖出订单已下单: {symbol}")
            
            if order:
                self.open_orders[order["id"]] = order
            
            return order
        except Exception as e:
            logger.error(f"卖出订单执行失败: {e}")
            return None

    def _simulate_order(
        self,
        exchange: str,
        symbol: str,
        side: str,
        amount: float,
        price: float,
    ) -> Dict:
        """
        模拟订单 (纸面交易)
        
        Args:
            exchange: 交易所
            symbol: 交易对
            side: 买卖方向
            amount: 数量
            price: 价格
            
        Returns:
            模拟订单字典
        """
        import uuid
        return {
            "id": str(uuid.uuid4()),
            "exchange": exchange,
            "symbol": symbol,
            "side": side,
            "amount": amount,
            "price": price,
            "status": "closed",
            "filled": amount,
            "timestamp": datetime.now().isoformat(),
        }

    def cancel_order(
        self, exchange: str, symbol: str, order_id: str
    ) -> Optional[Dict]:
        """
        取消订单
        
        Args:
            exchange: 交易所名称
            symbol: 交易对
            order_id: 订单 ID
            
        Returns:
            取消后的订单信息
        """
        if self.paper_trading:
            if order_id in self.open_orders:
                order = self.open_orders.pop(order_id)
                logger.info(f"✓ 模拟订单已取消: {order_id}")
                return order
            return None
        else:
            order = self.exchange_api.cancel_order(exchange, symbol, order_id)
            if order and order_id in self.open_orders:
                del self.open_orders[order_id]
            return order

    def get_order_status(
        self, exchange: str, symbol: str, order_id: str
    ) -> Optional[str]:
        """
        查询订单状态
        
        Args:
            exchange: 交易所名称
            symbol: 交易对
            order_id: 订单 ID
            
        Returns:
            订单状态 (open/closed/canceled)
        """
        if order_id in self.open_orders:
            return self.open_orders[order_id].get("status")
        
        if not self.paper_trading:
            order = self.exchange_api.get_order(exchange, symbol, order_id)
            if order:
                return order.get("status")
        
        return None

    def get_open_orders(self, exchange: str) -> List[Dict]:
        """
        获取所有未成交订单
        
        Args:
            exchange: 交易所名称
            
        Returns:
            未成交订单列表
        """
        if self.paper_trading:
            return [
                o for o in self.open_orders.values()
                if o.get("exchange") == exchange
            ]
        else:
            return self.exchange_api.get_open_orders(exchange) or []

    def get_execution_stats(self) -> Dict:
        """
        获取执行统计信息
        
        Returns:
            统计字典
        """
        return {
            "open_orders_count": len(self.open_orders),
            "closed_orders_count": len(self.closed_orders),
            "total_orders": len(self.open_orders) + len(self.closed_orders),
            "paper_trading": self.paper_trading,
            "trading_enabled": self.trading_enabled,
        }
