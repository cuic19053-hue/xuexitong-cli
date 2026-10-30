from setuptools import setup, find_packages

setup(
    name="xuexitong-cli",
    version="1.0.0",
    description="超星学习通纯逆向协议 CLI 工具（支持原速心跳守护 + DeepSeek AI 答题推理）",
    author="YourName",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
    ],
    entry_points={
        "console_scripts": [
            "xuexitong=xuexitong_cli.cli:main",
        ],
    },
    python_requires=">=3.8",
)
