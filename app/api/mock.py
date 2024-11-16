from fastapi import Request, Response, HTTPException
from fastapi.responses import StreamingResponse
import json
import asyncio
import time
from datetime import datetime
import logging
from typing import Dict, Any, Optional, List
from ..utils.helpers import create_response_data

logger = logging.getLogger(__name__)

class Mock:
    """Ollama API Mock 实现"""
    
    def __init__(self, db, api_client):
        """
        初始化 Mock
        
        Args:
            db: 数据库管理器
            api_client: API 客户端
        """
        self.db = db
        self.api_client = api_client

    async def chat(self, request: Request) -> StreamingResponse:
        """聊天完成响应"""
        data = await request.json()
        
        if not data.get("messages"):
            return Response(
                content=json.dumps(create_response_data(
                    model=data["model"],
                    done=True,
                    done_reason="load"
                )),
                media_type="application/json"
            )

        if data.get("stream") == False:
            # 非流式请求
            try:
                start_time = time.time_ns()
                # 获取所有提供商的模型映射
                model_mappings = self.db.get_model_mapping(data["model"])
                
                # 使用 async for 来获取生成器的第一个响应
                content = ""
                async for response in self.api_client.chat_completion(
                    model=model_mappings,  # 传递所有模型映射
                    messages=data["messages"],
                    stream=False
                ):
                    if not response["done"]:
                        content += response["message"]["content"]
                    else:
                        break
                
                return Response(
                    content=json.dumps(create_response_data(
                        model=data["model"],
                        content=content,
                        done=True,
                        total_duration=time.time_ns() - start_time
                    )),
                    media_type="application/json"
                )
            except Exception as e:
                logger.error(f"Chat error: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))

        async def stream_response():
            try:
                model_mappings = self.db.get_model_mapping(data["model"])
                logger.info(f"Model mappings for {data['model']}: {model_mappings}")
                
                async for response in self.api_client.chat_completion(
                    model=model_mappings,
                    messages=data["messages"]
                ):
                    response["model"] = data["model"]
                    yield json.dumps(response) + "\n"
                    
            except Exception as e:
                logger.error(f"Stream response error: {str(e)}")
                error_data = create_response_data(
                    model=data["model"],
                    content=str(e),
                    done=True,
                    done_reason="error"
                )
                yield json.dumps(error_data) + "\n"

        return StreamingResponse(
            stream_response(),
            media_type="application/x-ndjson",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            }
        )

    async def generate(self, request: Request) -> StreamingResponse:
        """生成完成响应"""
        return await self.chat(request)  # 复用 chat 接口

    async def create_model(self, request: Request) -> StreamingResponse:
        """创建新模型"""
        data = await request.json()
        model_data = {
            "name": data["name"],
            "modified_at": datetime.now().isoformat(),
            "size": 0,
            "digest": "",
            "details": data.get("details", {})
        }
        self.db.add_model(data["name"], model_data)
        
        async def stream_response():
            steps = [
                {"status": "reading model metadata"},
                {"status": "creating system layer"},
                {"status": "success"}
            ]
            for step in steps:
                yield json.dumps(step) + "\n"
                await asyncio.sleep(0.5)
                
        return StreamingResponse(
            stream_response(),
            media_type="text/event-stream"
        )

    async def list_models(self) -> Dict[str, List[Dict[str, Any]]]:
        """列出本地可用的模型"""
        try:
            return {"models": list(self.db.get_models_db().values())}
        except Exception as e:
            logger.error(f"List models error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def show_model(self, request: Request) -> Dict[str, Any]:
        """显示模型信息"""
        try:
            data = await request.json()
            model_name = data["model"]
            models_db = self.db.get_models_db()
            
            if model_name not in models_db:
                raise HTTPException(status_code=404, detail="Model not found")
                
            return {
                "modelfile": "FROM llama2\nSYSTEM You are a helpful assistant.",
                "parameters": "temperature 0.7\ntop_p 0.9",
                "template": "{{ .System }}\nUser: {{ .Prompt }}\nAssistant: {{ .Response }}",
                "details": models_db[model_name]["details"]
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Show model error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def copy_model(self, request: Request) -> Response:
        """复制模型"""
        try:
            data = await request.json()
            source = data["source"]
            destination = data["destination"]
            
            models_db = self.db.get_models_db()
            if source not in models_db:
                raise HTTPException(status_code=404, detail="Source model not found")
            
            # 复制模型数据
            model_data = models_db[source].copy()
            model_data["name"] = destination
            model_data["modified_at"] = datetime.now().isoformat()
            
            self.db.add_model(destination, model_data)
            return Response(status_code=200)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Copy model error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_model(self, request: Request) -> Response:
        """删除模型"""
        try:
            data = await request.json()
            model_name = data["model"]
            
            if model_name not in self.db.get_models_db():
                raise HTTPException(status_code=404, detail="Model not found")
                
            self.db.remove_model(model_name)
            return Response(status_code=200)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Delete model error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def pull_model(self, request: Request) -> StreamingResponse:
        """拉取模型"""
        try:
            data = await request.json()
            if data.get("stream") == False:
                return Response(
                    content=json.dumps({"status": "success"}),
                    media_type="application/json"
                )
            
            async def stream_response():
                total_size = 4661216384
                chunks = 3
                
                # 1. 拉取清单
                manifest_msg = json.dumps({"status": "pulling manifest"})
                yield f"data: {manifest_msg}\n\n"
                await asyncio.sleep(0.5)
                
                # 2. 下载进度
                for i in range(chunks):
                    completed = (total_size // chunks) * (i + 1)
                    download_msg = json.dumps({
                        'status': 'downloading',
                        'digest': 'sha256:8eeb52dfb3bb9aefdf9d1ef24b3bdbcfbe82238798c4b918278320b6fcef18fe',
                        'total': total_size,
                        'completed': completed
                    })
                    yield f"data: {download_msg}\n\n"
                    await asyncio.sleep(0.2)
                
                # 3. 验证
                verify_msg = json.dumps({"status": "verifying sha256 digest"})
                yield f"data: {verify_msg}\n\n"
                await asyncio.sleep(0.5)
                
                # 4. 完成
                success_msg = json.dumps({"status": "success"})
                yield f"data: {success_msg}\n\n"
            
            return StreamingResponse(
                stream_response(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "text/event-stream",
                    "X-Accel-Buffering": "no"
                }
            )
        except Exception as e:
            logger.error(f"Pull model error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def push_model(self, request: Request) -> StreamingResponse:
        """推送模型"""
        try:
            data = await request.json()
            
            async def stream_response():
                steps = [
                    {"status": "retrieving manifest"},
                    {"status": "pushing manifest"},
                    {"status": "success"}
                ]
                for step in steps:
                    yield json.dumps(step) + "\n"
                    await asyncio.sleep(1)
                    
            return StreamingResponse(
                stream_response(),
                media_type="text/event-stream"
            )
        except Exception as e:
            logger.error(f"Push model error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def generate_embeddings(self, request: Request) -> Dict[str, Any]:
        """生成嵌入向量"""
        try:
            data = await request.json()
            input_data = data["input"]
            model_name = data["model"]
            
            # 生成示嵌入向量
            sample_embedding = [0.1, -0.2, 0.3, 0.4, -0.5] * 2
            
            if isinstance(input_data, list):
                embeddings = [sample_embedding for _ in input_data]
            else:
                embeddings = [sample_embedding]
                
            return {
                "model": model_name,
                "embeddings": embeddings,
                "total_duration": 14143917,
                "load_duration": 1019500,
                "prompt_eval_count": 8
            }
        except Exception as e:
            logger.error(f"Generate embeddings error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def list_running_models(self) -> Dict[str, List[Dict[str, Any]]]:
        """列出正在运行的模型"""
        try:
            return {"models": list(self.db.get_running_models().values())}
        except Exception as e:
            logger.error(f"List running models error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e)) 