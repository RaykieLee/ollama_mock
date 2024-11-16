import os
import sys
from pathlib import Path
import uvicorn
from dotenv import load_dotenv
from app.core.logging import setup_logging

# 加载环境变量
load_dotenv()

# 添加项目根目录到 Python 路径
ROOT_DIR = Path(__file__).resolve().parent
sys.path.append(str(ROOT_DIR))

if __name__ == "__main__":
    # 设置日志
    setup_logging()
    
    # 运行服务器
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "11434")),
        reload=os.getenv("RELOAD", "true").lower() == "true",
        workers=int(os.getenv("WORKERS", "1")),
        log_config=None  # 使用自定义日志配置
    ) 