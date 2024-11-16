from datetime import datetime
from typing import Dict, Any, Optional

def create_response_data(
    model: str,
    content: str = "",
    done: bool = False,
    done_reason: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    创建标准响应数据
    
    Args:
        model: 模型名称
        content: 响应内容
        done: 是否完成
        done_reason: 完成原因
        **kwargs: 其他参数
    
    Returns:
        标准格式的响应数据
    """
    response = {
        "model": model,
        "created_at": datetime.now().isoformat(),
        "message": {
            "role": "assistant",
            "content": content
        },
        "done": done
    }
    
    if done_reason:
        response["done_reason"] = done_reason
        
    # 添加其他参数
    response.update(kwargs)
    
    return response

def format_duration(duration_ns: int) -> str:
    """
    格式化持续时间
    
    Args:
        duration_ns: 持续时间（纳秒）
    
    Returns:
        格式化后的持续时间字符串
    """
    duration_ms = duration_ns / 1_000_000  # 转换为毫秒
    if duration_ms < 1000:
        return f"{duration_ms:.2f}ms"
    duration_s = duration_ms / 1000  # 转换为秒
    if duration_s < 60:
        return f"{duration_s:.2f}s"
    duration_m = duration_s / 60  # 转换为分钟
    return f"{duration_m:.2f}m"

def format_size(size_bytes: int) -> str:
    """
    格式化文件大小
    
    Args:
        size_bytes: 文件大小（字节）
    
    Returns:
        格式化后的文件大小字符串
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f}{unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f}PB"

def create_error_response(
    error: Exception,
    model: str = "",
    status_code: int = 500
) -> Dict[str, Any]:
    """
    创建错误响应数据
    
    Args:
        error: 异常对象
        model: 模型名称
        status_code: HTTP状态码
    
    Returns:
        错误响应数据
    """
    return {
        "model": model,
        "created_at": datetime.now().isoformat(),
        "error": {
            "code": status_code,
            "message": str(error)
        },
        "done": True,
        "done_reason": "error"
    }

def validate_messages(messages: list) -> bool:
    """
    验证消息格式
    
    Args:
        messages: 消息列表
    
    Returns:
        是否有效
    """
    if not isinstance(messages, list):
        return False
    
    for message in messages:
        if not isinstance(message, dict):
            return False
        if "role" not in message or "content" not in message:
            return False
        if message["role"] not in ["system", "user", "assistant"]:
            return False
            
    return True 