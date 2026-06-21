"""
风险管理模块
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class RiskManager:
    """风险管理器"""
    
    def __init__(self, config: Dict, initial_balance: float):
        """
        初始化风险管理器
        
        Args:
            config: 配置字典
            initial_balance: 初始账户资金
        """
        self.config = config
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.max_position_size = config.get("MAX_POSITION_SIZE", 0.1)
        self.stop_loss_percent = config.get("STOP_LOSS_PERCENT", 0.02)
        self.take_profit_percent = config.get("TAKE_PROFIT_PERCENT", 0.05)
        self.max_daily_loss = config.get("DAILY_MAX_LOSS", 0.05)
        self.max_daily_drawdown = config.get("DAILY_MAX_DRAWDOWN", 0.1)
        self.risk_per_trade = config.get("RISK_PER_TRADE", 0.01)
        self.daily_pnl = 0
        self.positions = {}  # {symbol: position_info}
    
    def validate_trade(self, symbol: str, amount: float, price: float) -> Dict:
        """
        验证交易是否符合风险规则
        
        Args:
            symbol: 交易对
            amount: 交易数量
            price: 交易价格
            
        Returns:
            验证结果 {"valid": bool, "reason": str, "risk_level": str}
        """
        trade_value = amount * price
        max_trade_value = self.current_balance * self.max_position_size
        
        # 检查仓位大小
        if trade_value > max_trade_value:
            return {
                "valid": False,
                "reason": f"单笔交易 {trade_value:.2f} 超过最大仓位 {max_trade_value:.2f}",
                "risk_level": "critical",
            }
        
        # 检查每日亏损
        daily_loss_percent = abs(self.daily_pnl) / self.initial_balance
        if daily_loss_percent >= self.max_daily_loss:
            return {
                "valid": False,
                "reason": f"每日亏损已达上限 ({daily_loss_percent*100:.2f}%)",
                "risk_level": "critical",
            }
        
        # 检查风险百分比
        risk_amount = trade_value * self.risk_per_trade
        if risk_amount > self.current_balance * self.risk_per_trade:
            return {
                "valid": False,
                "reason": f"单笔风险 {risk_amount:.2f} 超过限制",
                "risk_level": "high",
            }
        
        return {
            "valid": True,
            "reason": "交易通过风险检查",
            "risk_level": "low",
        }
    
    def calculate_stop_loss(self, entry_price: float, side: str = "buy") -> float:
        """
        计算止损价格
        
        Args:
            entry_price: 入场价格
            side: 交易方向 (buy/sell)
            
        Returns:
            止损价格
        """
        if side == "buy":
            return entry_price * (1 - self.stop_loss_percent)
        else:  # sell
            return entry_price * (1 + self.stop_loss_percent)
    
    def calculate_take_profit(self, entry_price: float, side: str = "buy") -> float:
        """
        计算止盈价格
        
        Args:
            entry_price: 入场价格
            side: 交易方向 (buy/sell)
            
        Returns:
            止盈价格
        """
        if side == "buy":
            return entry_price * (1 + self.take_profit_percent)
        else:  # sell
            return entry_price * (1 - self.take_profit_percent)
    
    def update_position(self, symbol: str, side: str, amount: float, price: float):
        """
        更新持仓
        
        Args:
            symbol: 交易对
            side: 买卖方向
            amount: 数量
            price: 价格
        """
        if symbol not in self.positions:
            self.positions[symbol] = {
                "amount": 0,
                "avg_price": 0,
                "entry_time": None,
            }
        
        pos = self.positions[symbol]
        
        if side == "buy":
            # 增加持仓
            total_cost = pos["amount"] * pos["avg_price"] + amount * price
            pos["amount"] += amount
            pos["avg_price"] = total_cost / pos["amount"] if pos["amount"] > 0 else price
        else:  # sell
            # 减少持仓
            pos["amount"] -= amount
            if pos["amount"] <= 0:
                pos["amount"] = 0
                pos["avg_price"] = 0
    
    def check_stop_loss(self, symbol: str, current_price: float) -> bool:
        """
        检查是否触发止损
        
        Args:
            symbol: 交易对
            current_price: 当前价格
            
        Returns:
            是否触发止损
        """
        if symbol not in self.positions or self.positions[symbol]["amount"] == 0:
            return False
        
        pos = self.positions[symbol]
        stop_loss_price = self.calculate_stop_loss(pos["avg_price"], "buy")
        
        if current_price <= stop_loss_price:
            logger.warning(f"⚠️ {symbol} 触发止损! 当前价格 {current_price:.2f}, 止损价 {stop_loss_price:.2f}")
            return True
        
        return False
    
    def check_take_profit(self, symbol: str, current_price: float) -> bool:
        """
        检查是否触发止盈
        
        Args:
            symbol: 交易对
            current_price: 当前价格
            
        Returns:
            是否触发止盈
        """
        if symbol not in self.positions or self.positions[symbol]["amount"] == 0:
            return False
        
        pos = self.positions[symbol]
        take_profit_price = self.calculate_take_profit(pos["avg_price"], "buy")
        
        if current_price >= take_profit_price:
            logger.info(f"✓ {symbol} 触发止盈! 当前价格 {current_price:.2f}, 止盈价 {take_profit_price:.2f}")
            return True
        
        return False
    
    def get_position_value(self, symbol: str, current_price: float) -> float:
        """
        获取持仓价值
        
        Args:
            symbol: 交易对
            current_price: 当前价格
            
        Returns:
            持仓价值
        """
        if symbol not in self.positions:
            return 0
        return self.positions[symbol]["amount"] * current_price
    
    def get_unrealized_pnl(self, symbol: str, current_price: float) -> float:
        """
        获取未实现盈亏
        
        Args:
            symbol: 交易对
            current_price: 当前价格
            
        Returns:
            未实现盈亏
        """
        if symbol not in self.positions:
            return 0
        
        pos = self.positions[symbol]
        if pos["amount"] == 0:
            return 0
        
        entry_value = pos["amount"] * pos["avg_price"]
        current_value = pos["amount"] * current_price
        return current_value - entry_value
    
    def get_risk_metrics(self) -> Dict:
        """
        获取风险指标
        
        Returns:
            风险指标字典
        """
        return {
            "current_balance": self.current_balance,
            "initial_balance": self.initial_balance,
            "daily_pnl": self.daily_pnl,
            "max_position_size": self.max_position_size,
            "stop_loss_percent": self.stop_loss_percent,
            "take_profit_percent": self.take_profit_percent,
            "positions_count": len([p for p in self.positions.values() if p["amount"] > 0]),
        }
