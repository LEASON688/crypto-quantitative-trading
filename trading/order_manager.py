"""
订单管理模块
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class Order:
    """订单类"""
    
    def __init__(self, order_dict: Dict):
        self.id = order_dict.get("id")
        self.exchange = order_dict.get("exchange")
        self.symbol = order_dict.get("symbol")
        self.side = order_dict.get("side")  # buy/sell
        self.amount = order_dict.get("amount")
        self.price = order_dict.get("price")
        self.status = order_dict.get("status")  # open/closed/canceled
        self.filled = order_dict.get("filled", 0)
        self.timestamp = order_dict.get("timestamp")
    
    def is_fully_filled(self) -> bool:
        """是否全部成交"""
        return self.filled >= self.amount
    
    def is_expired(self, ttl_seconds: int = 3600) -> bool:
        """是否过期"""
        if not self.timestamp:
            return False
        order_time = datetime.fromisoformat(self.timestamp)
        return datetime.now() - order_time > timedelta(seconds=ttl_seconds)


class OrderManager:
    """订单管理器"""
    
    def __init__(self, config: Dict):
        """
        初始化订单管理器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.orders = {}  # {order_id: Order}
        self.order_history = []  # 订单历史
    
    def add_order(self, order_dict: Dict):
        """
        添加订单
        
        Args:
            order_dict: 订单字典
        """
        order = Order(order_dict)
        self.orders[order.id] = order
        self.order_history.append(order)
        logger.debug(f"订单已添加: {order.id}")
    
    def update_order(self, order_id: str, status: str, filled: float = 0):
        """
        更新订单状态
        
        Args:
            order_id: 订单 ID
            status: 新状态
            filled: 已成交数量
        """
        if order_id in self.orders:
            order = self.orders[order_id]
            order.status = status
            if filled > 0:
                order.filled = filled
            logger.debug(f"订单已更新: {order_id} -> {status}")
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """
        获取订单
        
        Args:
            order_id: 订单 ID
            
        Returns:
            订单对象
        """
        return self.orders.get(order_id)
    
    def get_open_orders(self) -> List[Order]:
        """
        获取所有未成交订单
        
        Returns:
            未成交订单列表
        """
        return [o for o in self.orders.values() if o.status == "open"]
    
    def get_orders_by_symbol(self, symbol: str) -> List[Order]:
        """
        获取特定币种的订单
        
        Args:
            symbol: 交易对
            
        Returns:
            订单列表
        """
        return [o for o in self.orders.values() if o.symbol == symbol]
    
    def get_orders_by_exchange(self, exchange: str) -> List[Order]:
        """
        获取特定交易所的订单
        
        Args:
            exchange: 交易所名称
            
        Returns:
            订单列表
        """
        return [o for o in self.orders.values() if o.exchange == exchange]
    
    def cancel_expired_orders(self, ttl_seconds: int = 3600):
        """
        取消过期订单
        
        Args:
            ttl_seconds: 订单生存时间
        """
        expired_orders = [
            o for o in self.orders.values()
            if o.status == "open" and o.is_expired(ttl_seconds)
        ]
        
        for order in expired_orders:
            order.status = "canceled"
            logger.info(f"订单已过期并取消: {order.id}")
    
    def get_statistics(self) -> Dict:
        """
        获取订单统计信息
        
        Returns:
            统计字典
        """
        open_orders = self.get_open_orders()
        closed_orders = [o for o in self.orders.values() if o.status == "closed"]
        
        return {
            "total_orders": len(self.orders),
            "open_orders": len(open_orders),
            "closed_orders": len(closed_orders),
            "total_buy_orders": len([o for o in self.orders.values() if o.side == "buy"]),
            "total_sell_orders": len([o for o in self.orders.values() if o.side == "sell"]),
        }
