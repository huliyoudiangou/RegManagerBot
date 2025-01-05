from app.utils.scheduler import get_scheduler
from app.utils.logger import logger
from app.utils.message_queue import get_message_queue
import telebot
from app.bot.core.bot_instance import bot
# 需要安装的模块：无

class MessageCleaner:
    """
    消息清理器
    """

    def __init__(self):
        self.scheduler = get_scheduler()
        self.bot = bot
        self.message_queue = get_message_queue()
    
    def _clean_messages(self):
      """清理消息"""
    #   if not self.bot:
    #        from app.bot.bot_manager import BotManager # 懒加载
    #        bot_manager = BotManager()
    #        self.bot = bot_manager.get_bot()
      messages_to_delete = self.message_queue.get_messages_to_delete()
      for chat_id, message_ids in messages_to_delete.items():
         for message_id in message_ids:
          try:
            self.bot.delete_message(chat_id=chat_id, message_id=message_id)
            logger.debug(f"定时清理消息成功, chat_id={chat_id}, message_id={message_id}")
          except telebot.apihelper.ApiTelegramException as e:
            logger.warning(f"定时清理消息失败: chat_id={chat_id}, message_id={message_id}, error={e}")
            
    
    def start(self):
      """启动定时清理任务"""
      self.scheduler.add_job(job_name="clean_message", interval=5, job_func=self._clean_messages)
      logger.info("启动消息清理器")
      
def create_message_cleaner():
    """创建MessageCleaner实例"""
    global _message_cleaner
    if not _message_cleaner:
       _message_cleaner = MessageCleaner()
    return _message_cleaner

_message_cleaner = None
def get_message_cleaner():
    """获取 MessageCleaner 实例"""
    global _message_cleaner
    if not _message_cleaner:
       _message_cleaner = create_message_cleaner()
    return _message_cleaner