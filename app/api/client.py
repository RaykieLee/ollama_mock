from openai import OpenAI
import logging
import time
import random
from typing import List, Dict, Any, AsyncGenerator
import asyncio
from ..core.config import ApiProvider

logger = logging.getLogger(__name__)

class Client:
    """API 客户端"""
    
    def __init__(self, providers: List[ApiProvider]):
        """
        初始化客户端
        
        Args:
            providers: API 提供商列表
        """
        self.providers = providers
        self.clients = {}
        for provider in providers:
            self.clients[provider.provider_name] = OpenAI(
                base_url=provider.base_url,
                api_key=provider.api_key,
                default_headers={
                    "HTTP-Referer": "http://localhost:11434",
                    "X-Title": "Ollama Mock Server",
                }
            )

    def _select_provider(self) -> ApiProvider:
        """
        选择一个可用的 API 提供商（加权轮询）
        """
        current_time = time.time()
        available_providers = []
        
        # 计算所有提供商中等待时间最短的
        min_wait_time = min(
            (1.0 / p.rate_limit) - (current_time - p.last_request_time)
            for p in self.providers
        )
        
        # 如果所有提供商都需要等待，直接返回等待时间最短的
        if min_wait_time > 0:
            return min(self.providers, key=lambda p: 
                (1.0 / p.rate_limit) - (current_time - p.last_request_time))
        
        # 只将当前可用的提供商添加到候选列表中
        for provider in self.providers:
            wait_time = (1.0 / provider.rate_limit) - (current_time - provider.last_request_time)
            if wait_time <= 0:
                available_providers.extend([provider] * provider.weight)
        
        if not available_providers:
            return min(self.providers, key=lambda p: 
                p.last_request_time + (1.0 / p.rate_limit))
            
        return random.choice(available_providers)

    async def chat_completion(
        self, 
        model: Dict[str, str],
        messages: list,
        stream: bool = True,
        **kwargs
    ) -> AsyncGenerator[Dict[Any, Any], None]:
        """调用 API 进行聊天补全"""
        while True:
            provider = self._select_provider()
            logger.info(f"Selected provider: {provider.provider_name}")
            
            current_time = time.time()
            # 计算等待时间，如果等待时间小于0，则不等待，直接请求，否则等待.等待时间为1/rate_limit - (当前时间 - 上次请求时间),rate 为 1000的时候，等待时间为1/1000 - (当前时间 - 上次请求时间)
            wait_time = (1.0 / provider.rate_limit) - (current_time - provider.last_request_time)
            
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            
            try:
                provider.last_request_time = time.time()
                client = self.clients[provider.provider_name]
                
                # 从映射中获取当前提供商的模型
                provider_model = model[provider.provider_name]
                
                stream = client.chat.completions.create(
                    model=provider_model,
                    messages=messages,
                    stream=True,
                    **kwargs
                )
                
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        yield {
                            "message": {
                                "role": "assistant",
                                "content": chunk.choices[0].delta.content
                            },
                            "done": False
                        }
                
                yield {
                    "message": {"role": "assistant", "content": ""},
                    "done": True,
                    "done_reason": "stop"
                }
                break
                
            except Exception as e:
                logger.error(f"Error with provider {provider.provider_name}: {str(e)}")
                # 如果有错误，尝试下一个提供商
                continue

    async def embeddings(self, model: str, input_text: str) -> Dict[str, Any]:
        """
        生成文本嵌入向量
        
        Args:
            model: 模型名称
            input_text: 输入文本
        
        Returns:
            嵌入向量数据
        """
        try:
            response = await self.client.embeddings.create(
                model=model,
                input=input_text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Embeddings error: {str(e)}")
            raise 