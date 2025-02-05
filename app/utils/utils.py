import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.utils.logger import logger
from app.utils.scheduler import get_scheduler
from app.bot.core.bot_instance import bot

# 需要安装的模块：无

scheduler = get_scheduler()


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
    if not data_list or page_size <= 0:
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


# 用于存储每个用户的分页状态
user_states = {}


def create_pagination(chat_id, user_list, items_per_page):
    if chat_id not in user_states:
        user_states[chat_id] = {
            'current_page': 1,
            'items_per_page': items_per_page,
            'user_list': user_list
        }

    state = user_states[chat_id]
    total_pages = (len(state['user_list']) + state['items_per_page'] - 1) // state['items_per_page']
    current_page = state['current_page']

    start_index = (current_page - 1) * state['items_per_page']
    end_index = min(start_index + state['items_per_page'], len(state['user_list']))
    items = state['user_list'][start_index:end_index]

    text = '\n'.join(map(str, items)) + f'\n\n当前页: {current_page}/{total_pages}页'

    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    if current_page > 1:
        markup.add(InlineKeyboardButton("⬅️ 上一页", callback_data='prev'))
    if current_page < total_pages:
        markup.add(InlineKeyboardButton("下一页 ➡️", callback_data='next'))

    return text, markup


@bot.callback_query_handler(func=lambda call: call.data in ['prev', 'next'])
def callback_inline(call):
    chat_id = call.message.chat.id
    # 确保用户状态存在
    if chat_id in user_states:
        if call.data == 'next':
            user_states[chat_id]['current_page'] += 1
        elif call.data == 'prev':
            user_states[chat_id]['current_page'] -= 1

        text, markup = create_pagination(
            chat_id,
            user_states[chat_id]['user_list'],
            user_states[chat_id]['items_per_page']
        )
        bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)


