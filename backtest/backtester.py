"""
回测框架
"""

import logging
from typing import Dict, List
import pandas as pd

logger = logging.getLogger(__name__)


class Backtester:
    """回测框架"""
    
    def __init__(self, config: Dict):
        """
        初始化回测器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.start_date = config.get("BACKTEST_START_DATE")
        self.end_date = config.get("BACKTEST_END_DATE")
        self.initial_balance = config.get("INITIAL_BALANCE", 10000)
        self.trades = []
        self.balance_history = [self.initial_balance]
    
    def run(self, df: pd.DataFrame, strategy) -> Dict:
        """
        运行回测
        
        Args:
            df: 包含 OHLCV 数据的 DataFrame
            strategy: 策略对象
            
        Returns:
            回测结果
        """
        logger.info(f"🔄 开始回测: {self.start_date} 至 {self.end_date}")
        
        current_balance = self.initial_balance
        position = None  # 当前持仓
        
        for idx, row in df.iterrows():
            signal = strategy.analyze(row.to_dict())
            
            # 生成交易信号
            if signal["signal"] == "BUY" and position is None:
                # 买入
                amount = current_balance / row["close"] * 0.95  # 保留 5% 现金
                entry_price = row["close"]
                position = {
                    "amount": amount,
                    "entry_price": entry_price,
                    "entry_time": idx,
                }
            
            elif signal["signal"] == "SELL" and position is not None:
                # 卖出
                exit_price = row["close"]
                profit = (exit_price - position["entry_price"]) * position["amount"]
                current_balance += profit + position["entry_price"] * position["amount"]
                
                self.trades.append({
                    "entry_time": position["entry_time"],
                    "entry_price": position["entry_price"],
                    "exit_time": idx,
                    "exit_price": exit_price,
                    "amount": position["amount"],
                    "profit": profit,
                })
                
                position = None
            
            self.balance_history.append(current_balance)
        
        logger.info(f"✓ 回测完成: 执行了 {len(self.trades)} 笔交易")
        
        return {
            "trades": self.trades,
            "final_balance": current_balance,
            "balance_history": self.balance_history,
        }
