import json
import threading
from datetime import datetime, timedelta
import logging
import os
from typing import Dict, Any, Optional
from ..core.config import settings

logger = logging.getLogger(__name__)

class Manager:
    """数据库管理器"""

    def __init__(self, file_path: str):
        """
        初始化数据库管理器
        
        Args:
            file_path: 数据库文件路径
        """
        self.file_path = os.path.join("data", file_path)
        self.lock = threading.Lock()
        self._ensure_data_dir()
        self._load_data()

    def _ensure_data_dir(self) -> None:
        """确保数据目录存在"""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def _load_data(self) -> None:
        """加载数据"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            logger.warning(f"Database file not found at {self.file_path}, creating new one")
            self.data = {
                "models_db": {},
                "running_models": {},
                "model_mappings": self._get_default_mappings()
            }
            self._save_data()
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from {self.file_path}: {str(e)}")
            raise

    def _save_data(self) -> None:
        """保存数据"""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving data to {self.file_path}: {str(e)}")
            raise

    def _get_default_mappings(self) -> Dict[str, str]:
        """获取默认的模型映射"""
        return {
            "llama2": "meta-llama/llama-3.2-3b-instruct:free",
            "mistral": "mistralai/mistral-7b",
            "codellama": "meta-llama/codellama-34b",
            "mixtral": "mistralai/mixtral-8x7b",
            "neural-chat": "anthropic/claude-3-opus",
            "openchat": "openchat/openchat-7b",
            "phi": "microsoft/phi-2",
            "qwen": "qwen/qwen-72b",
            "stable-beluga": "stabilityai/stable-beluga-7b"
        }

    def get_models_db(self) -> Dict[str, Any]:
        """获取模型数据库"""
        with self.lock:
            return self.data["models_db"]

    def get_running_models(self) -> Dict[str, Any]:
        """获取运行中的模型"""
        with self.lock:
            current_time = datetime.now()
            running_models = self.data["running_models"]
            
            # 更新过期时间
            for model in running_models.values():
                if model["expires_at"] is None:
                    model["expires_at"] = (current_time + timedelta(minutes=5)).isoformat()
                else:
                    # 检查是否过期
                    expires_at = datetime.fromisoformat(model["expires_at"])
                    if expires_at <= current_time:
                        model["expires_at"] = (current_time + timedelta(minutes=5)).isoformat()
            
            self._save_data()
            return running_models

    def get_model_mapping(self, ollama_model: str, provider_name: Optional[str] = None) -> str:
        """
        获取模型映射
        
        Args:
            ollama_model: Ollama 模型名称
            provider_name: API 提供商名称（可选）
        
        Returns:
            对应的模型名称
        """
        if provider_name:
            provider = settings.get_api_provider(provider_name)
            if provider:
                return provider.get_model(ollama_model)
            raise ValueError(f"Provider {provider_name} not found")
        
        # 如果没有指定提供商，返回所有提供商的映射
        return settings.get_model_mapping(ollama_model)

    def add_model(self, name: str, model_data: Dict[str, Any]) -> None:
        """
        添加模型
        
        Args:
            name: 模型名称
            model_data: 模型数据
        """
        with self.lock:
            self.data["models_db"][name] = model_data
            self._save_data()

    def remove_model(self, name: str) -> None:
        """
        删除模型
        
        Args:
            name: 模型名称
        """
        with self.lock:
            if name in self.data["models_db"]:
                del self.data["models_db"][name]
                self._save_data()

    def update_running_model(self, name: str, model_data: Dict[str, Any]) -> None:
        """
        更新运行中的模型
        
        Args:
            name: 模型名称
            model_data: 模型数据
        """
        with self.lock:
            self.data["running_models"][name] = model_data
            self._save_data()

    def update_model_mapping(self, ollama_model: str, openrouter_model: str) -> None:
        """
        更新模型映射
        
        Args:
            ollama_model: Ollama 模型名称
            openrouter_model: OpenRouter 模型名称
        """
        with self.lock:
            if "model_mappings" not in self.data:
                self.data["model_mappings"] = {}
            self.data["model_mappings"][ollama_model] = openrouter_model
            self._save_data() 