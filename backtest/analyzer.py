"""
性能分析模块
"""

import logging
from typing import Dict, List
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class Analyzer:
    """性能分析器"""
    
    @staticmethod
    def calculate_metrics(backtest_result: Dict, initial_balance: float) -> Dict:
        """
        计算性能指标
        
        Args:
            backtest_result: 回测结果
            initial_balance: 初始资金
            
        Returns:
            性能指标字典
        """
        trades = backtest_result.get("trades", [])
        balance_history = backtest_result.get("balance_history", [])
        final_balance = backtest_result.get("final_balance", initial_balance)
        
        if not balance_history:
            return {}
        
        # 总收益率
        total_return = (final_balance - initial_balance) / initial_balance
        
        # 年化收益率 (假设 365 天)
        annual_return = total_return * (365 / len(balance_history)) if len(balance_history) > 1 else 0
        
        # 最大回撤
        max_balance = max(balance_history)
        min_balance = min(balance_history)
        max_drawdown = (max_balance - min_balance) / max_balance if max_balance > 0 else 0
        
        # 交易统计
        if trades:
            profits = [t["profit"] for t in trades]
            winning_trades = len([p for p in profits if p > 0])
            losing_trades = len([p for p in profits if p < 0])
            win_rate = winning_trades / len(trades) if trades else 0
            avg_profit = sum(profits) / len(profits) if profits else 0
            
            # 利润因子
            total_profit = sum([p for p in profits if p > 0])
            total_loss = abs(sum([p for p in profits if p < 0]))
            profit_factor = total_profit / total_loss if total_loss > 0 else 0
        else:
            win_rate = 0
            avg_profit = 0
            profit_factor = 0
            winning_trades = 0
            losing_trades = 0
        
        # Sharpe 比率
        if len(balance_history) > 1:
            returns = pd.Series(balance_history).pct_change().dropna()
            sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
        else:
            sharpe_ratio = 0
        
        return {
            "total_return": total_return,
            "annual_return": annual_return,
            "max_drawdown": max_drawdown,
            "win_rate": win_rate,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "avg_profit": avg_profit,
            "profit_factor": profit_factor,
            "sharpe_ratio": sharpe_ratio,
            "total_trades": len(trades),
            "final_balance": final_balance,
        }
    
    @staticmethod
    def print_metrics(metrics: Dict):
        """
        打印性能指标
        
        Args:
            metrics: 性能指标字典
        """
        print("\n" + "="*50)
        print("📊 性能指标分析")
        print("="*50)
        print(f"总收益率: {metrics.get('total_return', 0)*100:.2f}%")
        print(f"年化收益: {metrics.get('annual_return', 0)*100:.2f}%")
        print(f"最大回撤: {metrics.get('max_drawdown', 0)*100:.2f}%")
        print(f"Sharpe比率: {metrics.get('sharpe_ratio', 0):.2f}")
        print(f"\n交易统计:")
        print(f"总交易数: {metrics.get('total_trades', 0)}")
        print(f"胜率: {metrics.get('win_rate', 0)*100:.2f}%")
        print(f"获利交易: {metrics.get('winning_trades', 0)}")
        print(f"亏损交易: {metrics.get('losing_trades', 0)}")
        print(f"平均利润: {metrics.get('avg_profit', 0):.2f}")
        print(f"利润因子: {metrics.get('profit_factor', 0):.2f}")
        print(f"\n最终账户: {metrics.get('final_balance', 0):.2f} USD")
        print("="*50 + "\n")
