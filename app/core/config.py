import os
from typing import Dict, Any, List, Optional
import yaml
import logging
from pydantic import Field
from pydantic_settings import BaseSettings
from functools import lru_cache

logger = logging.getLogger(__name__)

class ApiProvider(BaseSettings):
    provider_name: str
    base_url: str
    api_key: str
    rate_limit: float = 2.0
    weight: int = 1
    default_model: str
    provider_mappings: Dict[str, str] = {}
    last_request_time: float = 0.0

    def get_model(self, ollama_model: str) -> str:
        """获取对应的模型名称"""
        return self.provider_mappings.get(ollama_model, self.default_model)

    class Config:
        env_file = ".env"
        extra = "allow"

class ServerSettings(BaseSettings):
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=11434, env="PORT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    cors_origins: List[str] = Field(default=["*"])
    workers: int = Field(default=4, env="WORKERS")

    class Config:
        env_file = ".env"
        extra = "allow"

class Settings:
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "config/config.yaml"
        self._load_config()
        self._init_settings()

    def _load_config(self) -> None:
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading config file: {str(e)}")
            self.config = {}

    def _init_settings(self) -> None:
        providers_config = self.config.get("api_providers", [])
        self.api_providers = []
        
        for provider in providers_config:
            try:
                self.api_providers.append(ApiProvider(**provider))
            except Exception as e:
                logger.error(f"Error initializing provider {provider.get('provider_name')}: {str(e)}")
                continue

        self.server = ServerSettings(**self.config.get("server", {}))

    def get_api_provider(self, provider_name: str) -> Optional[ApiProvider]:
        """获取指定名称的 API 提供商配置"""
        for provider in self.api_providers:
            if provider.provider_name == provider_name:
                return provider
        return None

    def get_model_mapping(self, ollama_model: str) -> Dict[str, str]:
        """获取所有提供商对该模型的映射"""
        return {
            provider.provider_name: provider.get_model(ollama_model)
            for provider in self.api_providers
        }

settings = Settings() 