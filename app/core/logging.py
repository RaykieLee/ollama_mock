import logging
import logging.handlers
from pathlib import Path

def setup_logging():
    # 清除所有现有的处理器
    for logger_name in logging.root.manager.loggerDict:
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
    logging.getLogger().handlers.clear()
    
    # 基本配置
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_level = logging.INFO
    
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / "api.log",
        maxBytes=10*1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(logging.Formatter(log_format))
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # 特别处理 httpx 日志
    httpx_logger = logging.getLogger("httpx")
    httpx_logger.handlers = []  # 清除可能存在的处理器
    httpx_logger.propagate = True  # 让日志传递到根记录器
    
    # 设置其他模块的日志级别
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").handlers = []  # 清除 uvicorn 的处理器 