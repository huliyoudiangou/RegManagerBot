# 日志模块
from loguru import logger
from config import settings
import os
import sys

# 需要安装的模块：loguru
# pip install loguru

# 确保日志目录存在
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 配置 logger
logger.add(os.path.join(log_dir, "error.log"), rotation="10 MB", level="ERROR", format="{time} {level} {message}", backtrace=True, diagnose=True)  # 错误日志
logger.add(os.path.join(log_dir, "warning.log"), rotation="10 MB", level="WARNING", format="{time} {level} {message}")  # 警告日志
logger.add(os.path.join(log_dir, "info.log"), rotation="1 week", level="INFO", format="{time} {level} {message}")  # 信息日志
logger.add(os.path.join(log_dir, "debug.log"), rotation="1 week", level="DEBUG", format="{time} {level} {message}", backtrace=True, diagnose=True)  # 调试日志
logger.add(os.path.join(log_dir, "business.log"), rotation="1 week", level="INFO", format="{time} {level} {message}")  # 业务日志
logger.add(os.path.join(log_dir, "system.log"), rotation="1 week", level="INFO", format="{time} {level} {message}")  # 系统日志

logger.remove() # 移除默认控制台输出
logger.add(sys.stdout, level="INFO", format="{time} {level} {message}") # 添加控制台输出，级别为 INFO

# 使用示例
if __name__ == "__main__":
    logger.debug("这是一条调试日志")
    logger.info("这是一条信息日志")
    logger.warning("这是一条警告日志")
    logger.error("这是一条错误日志")
    try:
        1 / 0
    except Exception as e:
        logger.exception(f"捕获到异常: {e}")