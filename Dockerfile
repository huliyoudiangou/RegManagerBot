# 使用 Python 3.9 作为基础镜像
FROM python:3.9-slim-buster

# 定义 UID 和 GID
ARG UID=1000
ARG GID=1000

# 创建用户和用户组，并指定 UID 和 GID
RUN groupadd -g ${GID} bot && useradd -u ${UID} -g bot bot

USER bot
# 设置工作目录
WORKDIR /app

# 将当前目录的文件复制到容器的 /app 目录
COPY . /app

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 定义启动命令
CMD ["python", "main.py"]