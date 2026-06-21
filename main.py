"""
主程序入口
量化交易系统启动点
"""

import sys
import argparse
import logging
from datetime import datetime

# 导入各模块
from data.exchange_api import ExchangeAPI
from data.data_handler import DataHandler
from strategy.anomaly_detector import AnomalyDetector
from strategy.arbitrage_strategy import ArbitrageStrategy
from trading.executor import TradeExecutor
from trading.risk_manager import RiskManager
from monitoring.logger import setup_logger
from monitoring.monitor import Monitor
from monitoring.alerts import AlertManager
from backtest.backtester import Backtester
from backtest.analyzer import Analyzer


def load_config():
    """
    加载配置
    
    Returns:
        配置字典
    """
    try:
        import config
        return vars(config)
    except ImportError:
        print("❌ 配置文件不存在！请复制 config.example.py 为 config.py")
        print("   cp config.example.py config.py")
        sys.exit(1)


def setup_system(config: dict):
    """
    初始化系统
    
    Args:
        config: 配置字典
        
    Returns:
        系统组件字典
    """
    # 设置日志
    logger = setup_logger(config)
    logger.info("="*60)
    logger.info("🚀 加密货币量化交易系统启动")
    logger.info(f"📅 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*60)
    
    # 初始化各模块
    exchange_api = ExchangeAPI(config)
    data_handler = DataHandler(config)
    anomaly_detector = AnomalyDetector(config)
    arbitrage_strategy = ArbitrageStrategy(config)
    trade_executor = TradeExecutor(exchange_api, config)
    risk_manager = RiskManager(config, config.get("INITIAL_BALANCE", 10000))
    monitor = Monitor(config)
    alert_manager = AlertManager(config)
    
    logger.info("✓ 系统初始化完成")
    
    return {
        "logger": logger,
        "exchange_api": exchange_api,
        "data_handler": data_handler,
        "anomaly_detector": anomaly_detector,
        "arbitrage_strategy": arbitrage_strategy,
        "trade_executor": trade_executor,
        "risk_manager": risk_manager,
        "monitor": monitor,
        "alert_manager": alert_manager,
    }


def run_monitor_mode(system: dict, config: dict):
    """
    运行监控模式 (仅监控，不交易)
    
    Args:
        system: 系统组件
        config: 配置
    """
    logger = system["logger"]
    logger.info("\n" + "="*60)
    logger.info("📊 进入监控模式 (仅监控，不执行交易)")
    logger.info("="*60)
    
    alert_manager = system["alert_manager"]
    alert_manager.send_alert(
        "系统启动",
        "监控模式已启动，系统将实时监控市场异常波动",
        "info"
    )
    
    logger.info("💡 提示: 按 Ctrl+C 停止监控")
    logger.info("\n等待市场数据更新...\n")
    
    # TODO: 实现实时监控逻辑
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\n✓ 监控已停止")


def run_paper_trading_mode(system: dict, config: dict):
    """
    运行纸面交易模式 (模拟交易)
    
    Args:
        system: 系统组件
        config: 配置
    """
    logger = system["logger"]
    logger.info("\n" + "="*60)
    logger.info("📈 进入纸面交易模式 (模拟交易，不消费真实资金)")
    logger.info("="*60)
    
    alert_manager = system["alert_manager"]
    alert_manager.send_alert(
        "纸面交易开始",
        f"初始资金: {config.get('INITIAL_BALANCE', 10000)} USD",
        "info"
    )
    
    logger.info("💡 提示: 按 Ctrl+C 停止交易")
    logger.info("\n等待交易信号...\n")
    
    # TODO: 实现纸面交易逻辑
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\n✓ 纸面交易已停止")


def run_backtest_mode(system: dict, config: dict, args: argparse.Namespace):
    """
    运行回测模式
    
    Args:
        system: 系统组件
        config: 配置
        args: 命令行参数
    """
    logger = system["logger"]
    logger.info("\n" + "="*60)
    logger.info("📉 进入回测模式")
    logger.info("="*60)
    
    logger.info("💡 回测功能将在后续版本完善")


def run_live_trading_mode(system: dict, config: dict):
    """
    运行实盘交易模式 (真实交易)
    
    Args:
        system: 系统组件
        config: 配置
    """
    logger = system["logger"]
    logger.warning("\n" + "="*60)
    logger.warning("⚠️  进入实盘交易模式 (真实交易，谨慎操作!)")
    logger.warning("="*60)
    
    if not config.get("TRADING_ENABLED"):
        logger.error("❌ 实盘交易未启用！")
        logger.error("   请在 config.py 中设置: TRADING_ENABLED = True")
        sys.exit(1)
    
    # 确认警告
    logger.warning("\n⚠️  警告: 即将进入真实交易模式")
    logger.warning("   你的真实资金将被使用！")
    logger.warning("   请确保你已充分理解风险!")
    
    confirmation = input("\n输入 'YES' 确认开始实盘交易 (输入其他取消): ")
    if confirmation != "YES":
        logger.info("❌ 已取消实盘交易")
        sys.exit(0)
    
    logger.info("✓ 实盘交易已启动")
    logger.info("💡 提示: 按 Ctrl+C 停止交易")
    
    # TODO: 实现实盘交易逻辑
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\n✓ 实盘交易已停止")


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(
        description="🚀 加密货币量化交易系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py --mode monitor           # 启动监控模式
  python main.py --mode paper             # 启动纸面交易
  python main.py --mode live              # 启动实盘交易 (谨慎)
  python main.py --mode backtest          # 启动回测模式
        """
    )
    
    parser.add_argument(
        "--mode",
        type=str,
        default="monitor",
        choices=["monitor", "paper", "backtest", "live"],
        help="运行模式 (默认: monitor)"
    )
    
    parser.add_argument(
        "--test",
        action="store_true",
        help="测试模式 (用于调试)"
    )
    
    parser.add_argument(
        "--start-date",
        type=str,
        help="回测起始日期 (YYYY-MM-DD)"
    )
    
    parser.add_argument(
        "--end-date",
        type=str,
        help="回测结束日期 (YYYY-MM-DD)"
    )
    
    args = parser.parse_args()
    
    # 加载配置
    config = load_config()
    
    # 初始化系统
    system = setup_system(config)
    logger = system["logger"]
    
    # 根据模式运行
    try:
        if args.mode == "monitor":
            run_monitor_mode(system, config)
        elif args.mode == "paper":
            run_paper_trading_mode(system, config)
        elif args.mode == "backtest":
            run_backtest_mode(system, config, args)
        elif args.mode == "live":
            run_live_trading_mode(system, config)
    except KeyboardInterrupt:
        logger.info("\n\n" + "="*60)
        logger.info("✓ 系统已关闭")
        logger.info(f"📅 关闭时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*60)
    except Exception as e:
        logger.error(f"\n❌ 系统错误: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
