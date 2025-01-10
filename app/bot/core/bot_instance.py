import telebot
from app.utils import logger
from config.settings import TELEGRAM_BOT_TOKEN
from config.settings import DELAY_INTERVAL, ENABLE_MESSAGE_CLEANER
from app.utils.message_queue import get_message_queue
from app.utils.scheduler import get_scheduler

scheduler = get_scheduler()
message_queue = get_message_queue()
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# 保存原始的 send_message 和 reply_to 方法
original_send_message = bot.send_message
original_reply_to = bot.reply_to
original_register_next_step_handler = bot.register_next_step_handler

def send_message_with_delete(chat_id, text, delay=DELAY_INTERVAL, **kwargs):
    # 调用原始的 send_message 方法
    message = original_send_message(chat_id, text, **kwargs)
    if ENABLE_MESSAGE_CLEANER and delay is not None:
        message_queue.add_message(message, delay)
    return message

def reply_to_with_delete(message, text, delay=DELAY_INTERVAL, **kwargs):
    # 调用原始的 reply_to 方法
    reply_message = original_reply_to(message, text, **kwargs)
    if ENABLE_MESSAGE_CLEANER and delay is not None:
        message_queue.add_message(reply_message, delay)
    return reply_message

def register_next_step_handler_with_delete(message, callback, delay=30, **kwargs):
    # 调用原始的 register_next_step_handler 方法
    original_register_next_step_handler(message, callback, **kwargs)
    if ENABLE_MESSAGE_CLEANER and delay is not None:
        scheduler.add_delayed_job(delay, clear_step_handler, [message])

def clear_step_handler(message):
    bot.clear_step_handler(message)
    
bot.send_message = send_message_with_delete
bot.reply_to = reply_to_with_delete
bot.register_next_step_handler = register_next_step_handler_with_delete