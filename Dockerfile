# 使用 Python 3.11 作为基础镜像
FROM python:3.11-slim-bookworm

# 创建非 root 用户（假设用户名为appuser）
RUN useradd -m appuser

# 设置工作目录
WORKDIR /app

# 将当前目录的文件复制到容器的 /app 目录
COPY . /app

# 改变 /app 目录权限赋给appuser用户
RUN chown -R appuser:appuser /app

# 切换用户到appuser
USER appuser

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 定义启动命令
CMD ["python", "main.py"]