# Ollama Mock Server

这是一个模拟 Ollama API 的代理服务器，通过多个 API 提供商（如 OpenRouter、Groq、SambaNova、Together）来实现负载均衡和速率限制的大语言模型调用服务。
## 特点

- 兼容 [Ollama API](https://github.com/ollama/ollama/blob/main/docs/api.md) 接口
- 支持通过 OpenRouter、Groq、SambaNova、Together 调用主流大语言模型
- 支持流式响应
- 可配置的模型映射
- 完整的错误处理和日志记录

## 快速开始

### 安装

1. 克隆项目：
    ```bash
    git clone https://github.com/your-repo/ollama-mock-server.git
    ```
2. 安装依赖：
    ```bash
    pip install -e .
    ``` 
3. 配置 API 提供商：
    - 复制 `config/config.yaml.example` 文件为 `config/config.yaml`，并根据需要进行配置。
    - 配置文件中包含多个 API 提供商的配置，每个提供商可以有不同的权重和速率限制。

4. 运行服务器：
    ```bash
    python run.py
    ```
