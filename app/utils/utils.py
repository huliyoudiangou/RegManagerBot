from app.utils.logger import logger
from telebot.apihelper import ApiTelegramException

# 需要安装的模块：无

def paginate_list(data_list, page_size):
    """
    对列表进行分页

    Args:
        data_list: 要分页的列表
        page_size: 每页的条目数

    Returns:
         一个列表的列表，其中每个内部列表代表一页数据
    """
    logger.debug(f"开始分页列表, pageSize={page_size}, listSize={len(data_list)}")
    if not data_list or page_size <= 0 :
        logger.warning("列表为空或者分页大小不合法")
        return []
    
    paginated_list = []
    # if len(data_list) <= page_size:
    #     paginated_list.append(data_list)
    #     logger.debug(f"无需分页")
    # else:
    for i in range(0, len(data_list), page_size):
        paginated_list.append(data_list[i:i + page_size])
    logger.debug(f"分页列表成功, 总页数={len(paginated_list)}, pageSize={page_size}, listSize={len(data_list)}")
    return paginated_list

def paginate_list_text(data_list, page_size=None):
    if page_size is not None:
        return [data_list[i:i + page_size] for i in range(0, len(data_list), page_size)]

    # Default behavior when page_size is None: paginate based on 4096 byte limit
    result = []
    current_chunk = []
    current_length = 0

    for item in data_list:
        # Calculate the length of the current item plus newline character
        item_length = len(item) + 1  # 1 for the newline character

        # Check if adding this item would exceed the limit
        if current_length + item_length > 3600:
            # Append the current chunk to the result and reset
            result.append(current_chunk)
            current_chunk = []
            current_length = 0

        # Add the item to the current chunk
        current_chunk.append(item)
        current_length += item_length

    # Don't forget to add the last chunk if it's not empty
    if current_chunk:
        result.append(current_chunk)
    logger.debug(f"分页列表成功, 总页数={len(result)}, pageSize={page_size}, listSize={len(data_list)}")
    return result

def get_username_by_telegram_id(bot, chat_id, telegram_id):
    """
    根据 User ID 获取用户名

    Args:
        chat_id: 群组 ID
        telegram_id: 用户 ID

    Returns:
        Telegram 用户名，如果找不到用户则返回 None
    """
    logger.info(f"根据 Telegram ID 获取用户名: chat_id={chat_id}, telegram_id={telegram_id}")
    try:
        chat_member = bot.get_chat_member(chat_id, telegram_id)
        if chat_member and chat_member.user.username:
            logger.debug(f"获取 Telegram 用户名成功: telegram_id={telegram_id}, username={chat_member.user.username}")
            return chat_member.user.username
        else:
            logger.warning(f"未找到 Telegram 用户: telegram_id={telegram_id}")
            return None
    except ApiTelegramException as e:
        logger.error(f"获取 Telegram 用户名失败: telegram_id={telegram_id}, error={e}")
        return None


# def delete_message_after(bot, chat_id, message_id, delay):
#     """
#     在指定延迟后删除消息

#     Args:
#         bot: telebot 实例
#         chat_id: 聊天会话 ID
#         message_id: 消息 ID
#         delay: 延迟时间（秒）
#     """
#     def delete_messages():
#          try:
#            bot.delete_message(chat_id=chat_id, message_id=message_id)
#            logger.debug(f"删除消息成功: chat_id={chat_id}, message_id={message_id}")
#          except telebot.apihelper.ApiTelegramException as e:
#             logger.warning(f"删除消息失败, chat_id={chat_id}, message_id={message_id}, error={e}")
#     timer = threading.Timer(delay, delete_messages)
#     timer.daemon = True # 设置为守护进程，主进程关闭的时候，子进程也会关闭
#     timer.start()
    
# def send_message_with_auto_delete(bot, chat_id, text, delay=5, **kwargs):
#     """
#     发送自动删除的消息

#     Args:
#       bot: telebot 实例
#         chat_id: 聊天会话 ID
#         text: 消息文本
#         delay: 延迟删除的时间（秒），默认为 5 秒
#         **kwargs:  其他 send_message() 方法的参数
#     """
#     sent_message = bot.send_message(chat_id, text, **kwargs)
#     if sent_message:
#       delete_message_after(bot, sent_message.chat.id, sent_message.message_id, delay)
#       logger.debug(f"发送自动删除消息成功, chat_id={chat_id}, message_id={sent_message.message_id}, delay={delay}")
#     else:
#       logger.warning(f"发送自动删除消息失败, chat_id={chat_id}")