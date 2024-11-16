import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

@pytest.fixture
def mock_request_data():
    return {
        "model": "llama2",
        "messages": [
            {"role": "user", "content": "Hello"}
        ]
    }

def test_health_check():
    """测试健康检查接口"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_chat_endpoint(mock_request_data):
    """测试聊天接口"""
    response = client.post("/api/chat", json=mock_request_data)
    assert response.status_code == 200

def test_list_models():
    """测试列出模型接口"""
    response = client.get("/api/tags")
    assert response.status_code == 200
    assert "models" in response.json()

def test_show_model():
    """测试显示模型信息接口"""
    response = client.post("/api/show", json={"model": "llama2"})
    assert response.status_code == 200
    assert "modelfile" in response.json()
    assert "parameters" in response.json()
    assert "template" in response.json()
    assert "details" in response.json()

def test_model_not_found():
    """测试模型不存在的情况"""
    response = client.post("/api/show", json={"model": "nonexistent"})
    assert response.status_code == 404

def test_pull_model():
    """测试拉取模型接口"""
    response = client.post("/api/pull", json={"name": "llama2"})
    assert response.status_code == 200

def test_list_running_models():
    """测试列出运行中的模型接口"""
    response = client.get("/api/ps")
    assert response.status_code == 200
    assert "models" in response.json()

def test_generate_embeddings():
    """测试生成嵌入向量接口"""
    request_data = {
        "model": "llama2",
        "input": "Hello, world!"
    }
    response = client.post("/api/embed", json=request_data)
    assert response.status_code == 200
    assert "embeddings" in response.json()

# 添加更多测试... 