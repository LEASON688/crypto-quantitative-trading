"""
日志配置模块
"""

import logging
import os
from datetime import datetime
from pathlib import Path


def setup_logger(config: dict) -> logging.Logger:
    """
    设置日志系统
    
    Args:
        config: 配置字典
        
    Returns:
        Logger 对象
    """
    log_level = config.get("LOG_LEVEL", "INFO")
    log_dir = config.get("LOG_DIR", "./logs")
    log_to_file = config.get("LOG_TO_FILE", True)
    log_to_console = config.get("LOG_TO_CONSOLE", True)
    
    # 创建日志目录
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # 获取或创建 logger
    logger = logging.getLogger("crypto_trading")
    logger.setLevel(getattr(logging, log_level))
    
    # 日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台输出
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # 文件输出
    if log_to_file:
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(log_dir, f"trading_{today}.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger
