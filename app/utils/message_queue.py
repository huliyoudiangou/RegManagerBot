from app.utils.logger import logger
from datetime import datetime, timedelta

# 需要安装的模块：无


class Message:
    def __init__(self, chat_id, message_id, delay, create_time=None):
        self.chat_id = chat_id
        self.message_id = message_id
        self.delay = delay
        self.create_time = create_time if create_time else datetime.now()
        
_message_queue = None

class MessageQueue:
    """
    消息队列
    """

    def __init__(self):
        self.messages = {}

    def add_message(self, chat_id, message_id, delay=5):
        """添加待删除的消息"""
        if chat_id not in self.messages:
            self.messages[chat_id] = {}
        self.messages[chat_id][message_id] =  Message(chat_id=chat_id, message_id=message_id, delay=delay)
        logger.debug(f"添加待删除的消息, chat_id={chat_id}, message_id={message_id}, delay={delay}")

    def get_messages_to_delete(self):
        """获取需要删除的消息"""
        messages_to_delete = {}
        for chat_id, msgs in list(self.messages.items()):
          for message_id, message in list(msgs.items()):
            if (datetime.now() - message.create_time) > timedelta(seconds = message.delay):
               if chat_id not in messages_to_delete:
                 messages_to_delete[chat_id] = []
               messages_to_delete[chat_id].append(message_id)
               del self.messages[chat_id][message_id]

          if not msgs:
            del self.messages[chat_id]
        return messages_to_delete
    
    def get_all_messages(self):
        """获取所有消息，测试用"""
        return self.messages
    
def create_message_queue():
    """创建MessageQueue实例"""
    global _message_queue
    if not _message_queue:
       _message_queue = MessageQueue()
    return _message_queue

def get_message_queue():
    """获取 MessageQueue 实例"""
    global _message_queue
    if not _message_queue:
      _message_queue = create_message_queue()
    return _message_queue