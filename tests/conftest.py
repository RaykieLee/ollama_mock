import pytest
import os
import json
from app.db.manager import Manager
from app.api.client import Client
from app.core.config import settings

@pytest.fixture
def test_db():
    """创建测试数据库"""
    db_path = "data/test_db.json"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # 创建测试数据
    test_data = {
        "models_db": {
            "llama2": {
                "name": "llama2",
                "modified_at": "2024-01-20T10:00:00Z",
                "size": 3825819519,
                "digest": "test_digest",
                "details": {
                    "format": "gguf",
                    "family": "llama",
                    "parameter_size": "70B",
                    "quantization_level": "Q4_0"
                }
            }
        },
        "running_models": {},
        "model_mappings": {
            "llama2": "meta-llama/llama-2-70b-chat"
        }
    }
    
    # 写入测试数据
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    with open(db_path, 'w') as f:
        json.dump(test_data, f)
    
    db = Manager(db_path)
    yield db
    
    # 清理测试数据
    if os.path.exists(db_path):
        os.remove(db_path)

@pytest.fixture
def test_client():
    """创建测试 API 客户端"""
    return Client(
        api_key=settings.openrouter.api_key,
        site_url=settings.openrouter.site_url,
        app_name=settings.openrouter.app_name
    )

@pytest.fixture
def mock_response():
    """模拟 API 响应"""
    return {
        "model": "llama2",
        "created_at": "2024-03-19T12:00:00Z",
        "message": {
            "role": "assistant",
            "content": "Hello! How can I help you today?"
        },
        "done": True
    } 