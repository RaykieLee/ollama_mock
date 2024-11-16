import sys
from pathlib import Path

# 将项目根目录添加到 Python 路径
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.manager import Manager as DbManager
from app.api.client import Client as ApiClient
from app.api.mock import Mock as ApiMock

# 设置日志
setup_logging()
logger = logging.getLogger(__name__)

# 创建应用
app = FastAPI(
    title="Ollama Mock Server",
    description="A mock server for Ollama API",
    version="1.0.0"
)

# 添加 CORS 支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化组件
try:
    db = DbManager('db.json')
    api_client = ApiClient(providers=settings.api_providers)
    api_mock = ApiMock(db, api_client)
except Exception as e:
    logger.error(f"Failed to initialize components: {str(e)}")
    raise

# 路由定义
@app.post("/api/chat")
async def chat(request: Request):
    """聊天补全接口"""
    return await api_mock.chat(request)

@app.post("/api/generate")
async def generate(request: Request):
    """生成补全接口"""
    return await api_mock.generate(request)

@app.post("/api/create")
async def create(request: Request):
    """创建模型接口"""
    return await api_mock.create_model(request)

@app.get("/api/tags")
async def list_models():
    """列出模型接口"""
    return await api_mock.list_models()

@app.post("/api/show")
async def show_model(request: Request):
    """显示模型信息接口"""
    return await api_mock.show_model(request)

@app.post("/api/copy")
async def copy_model(request: Request):
    """复制模型接口"""
    return await api_mock.copy_model(request)

@app.delete("/api/delete")
async def delete_model(request: Request):
    """删除模型接口"""
    return await api_mock.delete_model(request)

@app.post("/api/pull")
async def pull_model(request: Request):
    """拉取模型接口"""
    return await api_mock.pull_model(request)

@app.post("/api/push")
async def push_model(request: Request):
    """推送模型接口"""
    return await api_mock.push_model(request)

@app.post("/api/embed")
async def generate_embeddings(request: Request):
    """生成嵌入向量接口"""
    return await api_mock.generate_embeddings(request)

@app.get("/api/ps")
async def list_running_models():
    """列出运行中的模型接口"""
    return await api_mock.list_running_models()

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}

if __name__ == "__main__":
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=11434,
            reload=True,
            log_config=None  # 使用我们自己的日志配置
        )
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        raise
