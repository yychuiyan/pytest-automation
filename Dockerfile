FROM python:3.11-slim

# 换国内源加速
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources

WORKDIR /app

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:0.12.5 /uv /usr/local/bin/uv

# 先复制依赖文件，利用 Docker 缓存层
COPY pyproject.toml uv.lock ./
COPY .python-version ./

ENV UV_DEFAULT_INDEX=https://mirrors.aliyun.com/pypi/simple/
RUN uv sync --frozen --no-dev

# 不复制业务代码，代码由 Jenkins checkout scm 拉取
