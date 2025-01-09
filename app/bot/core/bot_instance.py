import telebot
from app.utils import logger
from config.settings import TELEGRAM_BOT_TOKEN
from config.settings import DELAY_INTERVAL, ENABLE_MESSAGE_CLEANER
from app.utils.message_queue import get_message_queue

message_queue = get_message_queue()
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# 保存原始的 send_message 和 reply_to 方法
original_send_message = bot.send_message
original_reply_to = bot.reply_to

def send_message_with_delete(chat_id, text, delay=DELAY_INTERVAL, **kwargs):
    # 调用原始的 send_message 方法
    message = original_send_message(chat_id, text, **kwargs)
    if ENABLE_MESSAGE_CLEANER:
        if delay is not None:
            if delay >= 0:
                message_queue.add_message(message, delay)
            elif delay < 0:
                logger.debug(f"{chat_id} 的消息 {message.message_id} 将在 {abs(delay)} 秒后删除")
                message_queue.add_message(message, abs(delay))
                bot.clear_step_handler(message)
    return message

def reply_to_with_delete(message, text, delay=DELAY_INTERVAL, **kwargs):
    # 调用原始的 reply_to 方法
    reply_message = original_reply_to(message, text, **kwargs)
    if ENABLE_MESSAGE_CLEANER:
        if delay is not None:
            if delay >= 0:
                message_queue.add_message(reply_message, delay)
            elif delay < 0:
                logger.debug(f"{reply_message.message_id} 将在 {abs(delay)} 秒后删除")
                message_queue.add_message(reply_message, abs(delay))
                bot.clear_step_handler(reply_message)
    return reply_message

bot.send_message = send_message_with_delete
bot.reply_to = reply_to_with_delete