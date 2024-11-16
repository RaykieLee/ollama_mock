from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ollama_mock",
    version="1.0.0",
    author="",
    author_email="",
    description="A mock server for Ollama API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.109.2",
        "uvicorn>=0.27.1",
        "pyyaml>=6.0.1",
        "openai>=1.12.0",
        "python-multipart>=0.0.9",
        "pydantic>=2.6.3",
        "pydantic-settings>=2.2.1",
        "python-dotenv>=1.0.1",
        "pytest>=8.0.2",
        "requests>=2.31.0",
        "httpx>=0.27.0"
    ],
) 