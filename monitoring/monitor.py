"""
实时监控模块
"""

import logging
import asyncio
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class Monitor:
    """实时市场监控器"""
    
    def __init__(self, config: Dict):
        """
        初始化监控器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.update_interval = config.get("UPDATE_INTERVAL", 5)
        self.monitored_symbols = config.get("MONITOR_SYMBOLS", [])
        self.active_exchanges = config.get("ACTIVE_EXCHANGES", ["binance"])
        self.alerts = []  # 告警记录
        self.price_snapshots = {}  # 价格快照
        self.is_running = False
    
    def start(self, exchange_api, data_handler, anomaly_detector):
        """
        启动监控
        
        Args:
            exchange_api: 交易所 API
            data_handler: 数据处理器
            anomaly_detector: 异常检测器
        """
        self.exchange_api = exchange_api
        self.data_handler = data_handler
        self.anomaly_detector = anomaly_detector
        self.is_running = True
        logger.info("✓ 监控系统启动")
    
    def stop(self):
        """
        停止监控
        """
        self.is_running = False
        logger.info("✓ 监控系统已停止")
    
    def get_monitoring_summary(self) -> Dict:
        """
        获取监控摘要
        
        Returns:
            监控摘要字典
        """
        return {
            "is_running": self.is_running,
            "update_interval": self.update_interval,
            "symbols_count": len(self.monitored_symbols),
            "exchanges": self.active_exchanges,
            "alerts_count": len(self.alerts),
            "last_update": datetime.now().isoformat(),
        }
    
    def get_alerts(self, limit: int = 100) -> List[Dict]:
        """
        获取最近的告警
        
        Args:
            limit: 返回数量
            
        Returns:
            告警列表
        """
        return self.alerts[-limit:]
