from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import logging
import json
import httpx
from typing import Dict, Any
import time

# 配置日志格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()
OLLAMA_URL = "http://localhost:11434"

async def log_request(request: Request, body: Dict[Any, Any] = None):
    """记录请求信息"""
    headers = dict(request.headers)
    query_params = dict(request.query_params)
    
    log_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "method": request.method,
        "url": str(request.url),
        "path": request.url.path,
        "headers": headers,
        "query_params": query_params,
        "body": body
    }
    
    logger.info(f"收到请求:\n{json.dumps(log_data, ensure_ascii=False, indent=2)}")

@app.middleware("http")
async def log_middleware(request: Request, call_next):
    """记录所有请求的中间件"""
    # 读取请求体
    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        body_bytes = await request.body()
        try:
            body = json.loads(body_bytes)
        except:
            body = body_bytes.decode()
    
    # 记录请求
    await log_request(request, body)
    
    # 转发请求到实际的 Ollama 服务器
    async with httpx.AsyncClient() as client:
        target_url = f"{OLLAMA_URL}{request.url.path}"
        
        # 准备请求参数
        kwargs = {
            "method": request.method,
            "url": target_url,
            "headers": dict(request.headers),
            "params": dict(request.query_params),
        }
        
        if body is not None:
            if isinstance(body, dict):
                kwargs["json"] = body
            else:
                kwargs["data"] = body
        
        # 发送请求
        response = await client.request(**kwargs)
        
        # 如果是流式响应
        if "text/event-stream" in response.headers.get("content-type", ""):
            return StreamingResponse(
                response.aiter_bytes(),
                media_type="text/event-stream",
                headers=dict(response.headers)
            )
        
        return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=11434) 