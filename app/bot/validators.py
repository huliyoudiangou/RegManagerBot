# 校验器
from functools import wraps
from app.services.user_service import UserService
from app.services.invite_code_service import InviteCodeService
from app.utils.logger import logger
from datetime import datetime
from app.bot.core.bot_instance import bot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
# 需要安装的模块：无

def user_exists(service_name, negate=False):
    """
    验证用户是否存在于本地数据库的装饰器
     Args:
        service_name: 服务名称，例如 "navidrome"
        negate: 是否取反，默认为 False
    """
    def decorator(func):
        @wraps(func)
        def wrapper(message, *args, **kwargs):
            telegram_id = message.from_user.id
            logger.debug(f"校验用户是否存在于本地数据库: telegram_id={telegram_id}, service_name={service_name}, negate={negate}")

            user = UserService.get_user_by_telegram_id(telegram_id, service_name)
            
            if user and user.navidrome_user_id == None:
                logger.debug(f"已有积分用户，验证通过")
                # bot.reply_to(message, f"已有积分账户，请使用/use_code <邀请码>注册服务器即可")
                return func(message, *args, **kwargs)
                
            if (user and not negate) or (not user and negate):
                logger.debug(f"用户校验通过: telegram_id={telegram_id}, service_name={service_name}, negate={negate}, user_exists={bool(user)}")
                return func(message, *args, **kwargs)
            else:
                logger.warning(f"用户校验失败: telegram_id={telegram_id}, service_name={service_name}, negate={negate}, user_exists={bool(user)}")
                bot.reply_to(message, "未找到您的账户信息!" if not negate else "您已注册，请勿重复注册！如想重新注册，请先执行/deleteuser删除本地用户再注册!")
                return

        return wrapper
    return decorator

def admin_required(func):
    """
    验证用户是否是管理员的装饰器
    """
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        telegram_id = message.from_user.id # 修改获取 telegram_id 的方式
        logger.debug(f"校验用户是否是管理员: telegram_id={telegram_id}")
        if UserService.is_admin(telegram_id):
            logger.debug(f"用户是管理员: telegram_id={telegram_id}")
            return func(message, *args, **kwargs)
        else:
            logger.warning(f"用户不是管理员: telegram_id={telegram_id}")
            bot.reply_to(message, "你没有权限执行此操作!")
            return
    return wrapper

def invite_code_valid(func):
    """
    验证邀请码是否有效的装饰器
    """
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        # 通过消息的文本内容获取邀请码
        code = message.text.split(" ")[1] if len(message.text.split(" ")) > 1 else None

        logger.debug(f"校验邀请码是否有效: code={code}")
        if not code:
            logger.warning("未提供邀请码")
            bot.reply_to(message, "请提供邀请码!")
            return

        invite_code = InviteCodeService.get_invite_code(code)
        if invite_code and not invite_code.is_used and invite_code.expire_time > datetime.now():
            logger.debug(f"邀请码有效: code={code}")
            return func(message, *args, **kwargs)
        else:
            logger.warning(f"邀请码无效: code={code}")
            bot.reply_to(message, "邀请码无效!")
            return

    return wrapper

def score_enough(service_name):
    """
    验证用户积分是否足够的装饰器

    Args:
        service_name: 服务名称
    """
    def decorator(func):
        @wraps(func)
        def wrapper(message, *args, **kwargs):
            telegram_id = message.from_user.id  # 修改获取 telegram_id 的方式
            # 通过消息的文本内容获取需要的积分数量
            required_score = int(message.text.split(" ")[1]) if len(message.text.split(" ")) > 1 else 0

            logger.debug(f"校验用户积分是否足够: telegram_id={telegram_id}, required_score={required_score}")
            user = UserService.get_user_by_telegram_id(telegram_id, service_name)

            if user and user.score >= required_score:
                logger.debug(f"用户积分足够: telegram_id={telegram_id}, score={user.score}, required_score={required_score}")
                return func(message, *args, **kwargs)
            else:
                logger.warning(f"用户积分不足: telegram_id={telegram_id}, score={user.score if user else 0}, required_score={required_score}")
                bot.reply_to(message, "积分不足!")
                return

        return wrapper
    return decorator

# def confirmation_required(message_text):
#     """
#     要求用户确认的装饰器

#     Args:
#         message_text: 提示信息
#     """
#     def decorator(func):
#         @wraps(func)
#         def wrapper(message, *args, **kwargs):
            
#             keyboard = InlineKeyboardMarkup(
#                 [
#                     [InlineKeyboardButton("是", callback_data="confirm_yes"),
#                     InlineKeyboardButton("否", callback_data="confirm_no")]
#                 ]
#             )
#             sent_message = bot.reply_to(message, message_text, reply_markup=keyboard)
            
#             bot.register_callback_query_handler(
#                 lambda call: call.message.id == sent_message.id, # 只有当前消息触发的回调才会生效
#                 lambda call: _handle_confirmation_callback(call, func, message, sent_message, message_text, *args, **kwargs)
#                 )
#         return wrapper
#     return decorator


# def _handle_confirmation_callback(call, func, message, sent_message, message_text, *args, **kwargs):
#     """
#     处理按钮点击回调
#     """
#     bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=None) #移除按钮
#     if call.data == "confirm_yes":
#         bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
#         return func(message, *args, **kwargs)
#     elif call.data == "confirm_no":
#         if call.message.text != f"已取消：{message_text}":
#             bot.edit_message_text(text=f"已取消：{message_text}", chat_id=call.message.chat.id, message_id=call.message.id)
#         logger.debug("用户取消了操作")
#         return
    
# 用于存储用户会话信息
user_sessions = {}

def confirmation_required(message_text):
    def decorator(func):
        @wraps(func)
        def wrapper(message, *args, **kwargs):
            chat_id = message.chat.id

            # 创建内联键盘
            markup = InlineKeyboardMarkup()
            button_yes = InlineKeyboardButton("是", callback_data=f"confirm_yes_{chat_id}")
            button_no = InlineKeyboardButton("否", callback_data=f"confirm_no_{chat_id}")
            markup.add(button_yes, button_no)

            # 发送自定义的确认消息和键盘
            msg = bot.send_message(chat_id, message_text, reply_markup=markup)

            # 保存当前的命令函数和参数到会话
            user_sessions[chat_id] = {'message': message, 'func': func, 'args': args, 'kwargs': kwargs}

        return wrapper
    return decorator

@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm'))
def callback_query(call):
    chat_id = call.message.chat.id
    data = call.data

    if chat_id in user_sessions:
        # 获取存储的函数信息
        command_info = user_sessions[chat_id]
        message = command_info['message']
        func = command_info['func']
        args = command_info['args']
        kwargs = command_info['kwargs']

        if data == f"confirm_yes_{chat_id}":
            # 用户选择“是”，执行原始命令
            func(message, *args, **kwargs)
            logger.debug("已确认，命令已执行")
        elif data == f"confirm_no_{chat_id}":
            # 用户选择“否”，取消操作
            logger.debug("已取消，命令已取消")

        # 清除会话信息
        del user_sessions[chat_id]

    bot.answer_callback_query(call.id)