"""
告警系统模块
"""

import logging
import smtplib
from typing import Dict, List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import requests

logger = logging.getLogger(__name__)


class AlertManager:
    """告警管理器"""
    
    def __init__(self, config: Dict):
        """
        初始化告警管理器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.email_enabled = config.get("ALERT_EMAIL_ENABLED", False)
        self.dingtalk_enabled = config.get("ALERT_DINGTALK_ENABLED", False)
        self.alert_on_trade = config.get("ALERT_ON_TRADE", True)
        self.alert_on_signal = config.get("ALERT_ON_SIGNAL", True)
        self.alert_on_error = config.get("ALERT_ON_ERROR", True)
        self.alert_history = []  # 告警历史
    
    def send_alert(self, title: str, message: str, level: str = "info"):
        """
        发送告警
        
        Args:
            title: 告警标题
            message: 告警内容
            level: 告警级别 (info/warning/error)
        """
        alert = {
            "timestamp": datetime.now().isoformat(),
            "title": title,
            "message": message,
            "level": level,
        }
        self.alert_history.append(alert)
        
        logger.info(f"📢 {title}: {message}")
        
        # 发送邮件
        if self.email_enabled:
            self._send_email_alert(title, message)
        
        # 发送钉钉
        if self.dingtalk_enabled:
            self._send_dingtalk_alert(title, message, level)
    
    def _send_email_alert(self, title: str, message: str):
        """
        发送邮件告警
        
        Args:
            title: 邮件标题
            message: 邮件内容
        """
        try:
            if not self.config.get("ALERT_EMAIL_FROM"):
                logger.debug("邮件告警未配置")
                return
            
            msg = MIMEMultipart()
            msg["From"] = self.config.get("ALERT_EMAIL_FROM")
            msg["To"] = ", ".join(self.config.get("ALERT_EMAIL_TO", []))
            msg["Subject"] = f"[交易系统告警] {title}"
            
            msg.attach(MIMEText(message, "plain"))
            
            # 发送邮件
            smtp = smtplib.SMTP(self.config.get("ALERT_EMAIL_SMTP"), self.config.get("ALERT_EMAIL_PORT"))
            smtp.starttls()
            smtp.login(
                self.config.get("ALERT_EMAIL_FROM"),
                self.config.get("ALERT_EMAIL_PASSWORD")
            )
            smtp.send_message(msg)
            smtp.quit()
            
            logger.debug(f"✓ 邮件告警已发送")
        except Exception as e:
            logger.error(f"发送邮件告警失败: {e}")
    
    def _send_dingtalk_alert(self, title: str, message: str, level: str = "info"):
        """
        发送钉钉告警
        
        Args:
            title: 告警标题
            message: 告警内容
            level: 告警级别
        """
        try:
            webhook = self.config.get("ALERT_DINGTALK_WEBHOOK")
            if not webhook:
                logger.debug("钉钉告警未配置")
                return
            
            # 钉钉消息格式
            data = {
                "msgtype": "text",
                "text": {
                    "content": f"【{title}】\n{message}\n\n级别: {level}\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            }
            
            response = requests.post(webhook, json=data, timeout=5)
            if response.status_code == 200:
                logger.debug(f"✓ 钉钉告警已发送")
            else:
                logger.error(f"钉钉告警发送失败: {response.status_code}")
        except Exception as e:
            logger.error(f"发送钉钉告警失败: {e}")
    
    def send_trade_alert(self, exchange: str, symbol: str, side: str, amount: float, price: float):
        """
        发送交易告警
        
        Args:
            exchange: 交易所
            symbol: 交易对
            side: 买卖方向
            amount: 数量
            price: 价格
        """
        if not self.alert_on_trade:
            return
        
        title = f"{side.upper()} {symbol}"
        message = f"交易所: {exchange}\n交易对: {symbol}\n方向: {side.upper()}\n数量: {amount}\n价格: {price}"
        self.send_alert(title, message, "info")
    
    def send_signal_alert(self, symbol: str, signal_type: str, reason: str):
        """
        发送信号告警
        
        Args:
            symbol: 交易对
            signal_type: 信号类型 (buy/sell)
            reason: 原因
        """
        if not self.alert_on_signal:
            return
        
        title = f"{signal_type.upper()} {symbol}"
        message = f"交易对: {symbol}\n信号: {signal_type.upper()}\n原因: {reason}"
        self.send_alert(title, message, "info")
    
    def send_error_alert(self, error_message: str):
        """
        发送错误告警
        
        Args:
            error_message: 错误信息
        """
        if not self.alert_on_error:
            return
        
        title = "系统错误"
        message = error_message
        self.send_alert(title, message, "error")
    
    def get_alert_history(self, limit: int = 100) -> List[Dict]:
        """
        获取告警历史
        
        Args:
            limit: 返回数量
            
        Returns:
            告警历史列表
        """
        return self.alert_history[-limit:]
