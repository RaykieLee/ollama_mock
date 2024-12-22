import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging():
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # 文件处理器
    try:
        file_handler = RotatingFileHandler(
            filename=log_dir / "api.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            delay=True  # 延迟创建文件，直到第一次写入
        )
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        root_logger.addHandler(file_handler)
    except PermissionError:
        print("警告: 无法创建日志文件，将只输出到控制台")
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    root_logger.addHandler(console_handler)
    
    # 特别处理 httpx 日志
    httpx_logger = logging.getLogger("httpx")
    httpx_logger.handlers = []  # 清除可能存在的处理器
    httpx_logger.propagate = True  # 让日志传递到根记录器
    
    # 设置其他模块的日志级别
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").handlers = []  # 清除 uvicorn 的处理器 