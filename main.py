from app.utils.db_utils import create_tables
from app.bot.bot_manager import run_bot
from config import settings
from app.utils.logger import logger
from app.utils.scheduler import create_scheduler
from app.utils.message_queue import create_message_queue
from app.utils.message_cleaner import create_message_cleaner
from app.utils.mailu import create_mailu
# 需要安装的模块：无

        
def init_app():
    """初始化应用"""
    logger.info("初始化应用...")
    
    # 创建数据库表
    create_tables()
    logger.info("数据库表创建完成")
    
    scheduler = create_scheduler()
    scheduler.start_scheduler()
    logger.info(f"定时器已启动！")
    
    create_message_queue()
    logger.info(f"消息管理队列已启动！")
    
    create_mailu()
    logger.info(f"邮件注册系统已开启")
    
    if settings.ENABLE_MESSAGE_CLEANER:
        message_cleaner = create_message_cleaner()
        message_cleaner.start()
        logger.info(f"消息清理任务自动清理已开启！")
    
    logger.info(f"邀请码系统已{'开启' if settings.INVITE_CODE_SYSTEM_ENABLED else '关闭'}")
    logger.info(f"定时清理用户系统已{'开启' if settings.ENABLE_EXPIRED_USER_CLEAN else '关闭'}")
    logger.info("初始化完成")

if __name__ == "__main__":
    init_app()   
    run_bot()