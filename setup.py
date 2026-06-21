"""
项目安装配置
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="crypto-quantitative-trading",
    version="0.1.0",
    author="LEASON688",
    description="一个基于 Python 的加密货币量化交易系统，支持多交易所套利和异常波动交易",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LEASON688/crypto-quantitative-trading",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
)
