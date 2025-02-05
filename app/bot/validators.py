# 校验器
from functools import wraps
from app.services.user_service import UserService
from app.services.invite_code_service import InviteCodeService
from app.utils.logger import logger
from datetime import datetime, timedelta
from app.bot.core.bot_instance import bot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.utils.message_queue import get_message_queue
from config import settings

message_queue = get_message_queue()


def user_exists(negate=True):
    """
    一个装饰器，用于检查用户是否存在，并可以配置是否取反。
    如果 check_exist 为 True (默认)，则当用户存在时，允许执行被装饰的函数；不存在时，拒绝执行。
    如果 check_exist 为 False，则当用户不存在时，允许执行被装饰的函数；存在时，拒绝执行。
    """

    def decorator(func):
        @wraps(func)
        def wrapper(message, *args, **kwargs):
            telegram_id = message.from_user.id
            logger.debug(f"校验用户是否存在: telegram_id={telegram_id}")

            user = UserService.get_user_by_telegram_id(telegram_id=telegram_id)

            if user:
                if negate:
                    # 用户存在且 check_exist=True，允许执行
                    logger.warning(f"用户存在且允许执行: telegram_id={telegram_id}")
                    return func(message, *args, **kwargs)
                else:
                    # 已经注册过本地用户
                    if user.invite_code:
                        logger.info(f"用户使用过邀请码: telegram_id={telegram_id}")
                        return func(message, *args, **kwargs)

                    if user.username and not user.service_user_id:
                        logger.info(f"积分用户: telegram_id={telegram_id}")
                        return func(message, *args, **kwargs)
                    # 用户存在但 check_exist=False，拒绝执行
                    logger.info(f"用户存在但不允许执行: telegram_id={telegram_id}")
                    bot.reply_to(message, "用户已存在，操作不允许！")
                    return
            else:
                if negate:
                    # 用户不存在但 check_exist=True，拒绝执行
                    logger.info(f"用户不存在且不允许执行: telegram_id={telegram_id}")
                    bot.reply_to(message, "用户不存在，操作不允许！")
                    return
                else:
                    # 用户不存在且 check_exist=False，允许执行
                    logger.info(f"用户不存在且允许执行: telegram_id={telegram_id}")
                    return func(message, *args, **kwargs)

        return wrapper

    return decorator


def admin_required(func):
    """
    验证用户是否是管理员的装饰器
    """

    @wraps(func)
    def wrapper(message, *args, **kwargs):
        telegram_id = message.from_user.id  # 修改获取 telegram_id 的方式
        logger.debug(f"校验用户是否是管理员: telegram_id={telegram_id}")
        if UserService.is_admin(telegram_id):
            logger.debug(f"用户是管理员: telegram_id={telegram_id}")
            return func(message, *args, **kwargs)
        else:
            logger.warning(f"用户不是管理员: telegram_id={telegram_id}")
            bot.reply_to(message, "你没有权限执行此操作!")
            return

    return wrapper


def invite_system_enabled(func):
    """
    邀请系统是否开启的校验装饰器
    """

    @wraps(func)
    def wrapper(message, *args, **kwargs):
        # 检查邀请系统是否开启
        if not settings.INVITE_CODE_SYSTEM_ENABLED:
            logger.debug("邀请系统未开启，跳过邀请码验证")
            return func(message, *args, **kwargs)

        # 如果邀请系统开启，继续执行原逻辑
        logger.debug("邀请系统已开启，继续执行邀请码验证")
        bot.reply_to(message, "邀请系统已开启，请使用邀请码注册")
        return

    return wrapper


def invite_code_valid(func):
    """
    验证邀请码是否有效的装饰器
    """

    @wraps(func)
    def wrapper(message, *args, **kwargs):

        code = message.text.strip()
        logger.debug(f"校验邀请码是否有效: code={code}")
        if not code:
            logger.warning("未提供邀请码")
            bot.reply_to(message, "请提供邀请码!")
            return

        # 验证邀请码
        invite_code = InviteCodeService.get_invite_code(code)
        expire_time = invite_code.create_time + timedelta(days=invite_code.expire_days)

        if invite_code and not invite_code.is_used and expire_time > datetime.now():
            logger.debug(f"邀请码有效: code={code}")
            # 邀请码有效，继续执行原函数
            return func(message, *args, **kwargs)
        else:
            logger.warning(f"邀请码无效: code={code}")
            bot.reply_to(message, "邀请码无效!")
            return

    return wrapper


def score_enough():
    """
    验证用户积分是否足够的装饰器

    Args:
        service_type: 服务名称
    """

    def decorator(func):
        @wraps(func)
        def wrapper(message, *args, **kwargs):
            telegram_id = message.from_user.id  # 修改获取 telegram_id 的方式
            # 通过消息的文本内容获取需要的积分数量
            required_score = int(message.text.split(" ")[-1]) if len(message.text.split(" ")) > 1 else 0

            logger.debug(f"校验用户积分是否足够: telegram_id={telegram_id}, required_score={required_score}")
            user = UserService.get_user_by_telegram_id(telegram_id=telegram_id)

            if user and user.score >= required_score:
                logger.debug(
                    f"用户积分足够: telegram_id={telegram_id}, score={user.score}, required_score={required_score}")
                return func(message, *args, **kwargs)
            else:
                logger.warning(
                    f"用户积分不足: telegram_id={telegram_id}, score={user.score if user else 0}, required_score={required_score}")
                bot.reply_to(message, "积分不足!")
                return

        return wrapper

    return decorator


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
            bot.send_message(chat_id, message_text, reply_markup=markup)
            # logger.info(f"msg: {msg.message_id}")
            # logger.info(f"yes: {message.message_id}")
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
        bot.delete_message(chat_id, call.message.message_id)
        # if settings.ENABLE_MESSAGE_CLEANER:
        #     message_queue.add_message(user_sessions[chat_id]['message'])
        del user_sessions[chat_id]

    bot.answer_callback_query(call.id)
    if settings.ENABLE_MESSAGE_CLEANER:
        message_queue.add_message(call.message)


def private_chat_only(func):
    """
    限制命令只能在私聊中使用的装饰器
    """

    @wraps(func)
    def wrapper(message, *args, **kwargs):
        telegram_id = message.from_user.id  # 获取 telegram_id
        if message.chat.type in ["group", "supergroup"]:  # 群组或超级群组
            logger.debug(f"在群组中收到命令，不响应: chat_id={message.chat.id}, telegram_id={telegram_id}")
            return  # 在群组中不执行任何操作
        else:
            logger.debug(f"在私聊中收到命令，正常响应: chat_id={message.chat.id}, telegram_id={telegram_id}")
            return func(message, *args, **kwargs)

    return wrapper


def chat_type_required(not_chat_type=None):
    """
    限制命令只能在非指定 chat_type 使用的装饰器

    Args:
      not_chat_type: str | list 指定不允许的chat_type, 例如: ["private", "group", "supergroup"]
    """

    def decorator(func):
        @wraps(func)
        def wrapper(message, *args, **kwargs):
            telegram_id = message.from_user.id
            if not_chat_type:
                if isinstance(not_chat_type, str):
                    not_chat_type_list = [not_chat_type]
                else:
                    not_chat_type_list = not_chat_type
                if message.chat.type in not_chat_type_list:  # 群组或超级群组
                    logger.debug(
                        f"在{not_chat_type}中收到命令，不响应: chat_id={message.chat.id}, telegram_id={telegram_id}")
                    return
            logger.debug(
                f"在{message.chat.type}中收到命令，正常响应: chat_id={message.chat.id}, telegram_id={telegram_id}")
            return func(message, *args, **kwargs)

        return wrapper

    return decorator


def user_status_required(status=None):
    """
    限制命令不能在指定用户状态下使用的装饰器
    """

    if status is None:
        status = ["active", "whitelist"]

    def decorator(func):
        @wraps(func)
        def wrapper(message, *args, **kwargs):
            telegram_id = message.from_user.id
            user = UserService.get_user_by_telegram_id(telegram_id=telegram_id)
            if user and user.status in status:
                logger.debug(f"用户状态为{status}，允许执行: telegram_id={telegram_id}")
                return func(message, *args, **kwargs)
            elif user and user.status == "blocked":
                logger.warning(f"用户状态为blocked，不允许执行: telegram_id={telegram_id}")
                bot.send_message(message.chat.id, "你已被封禁，请联系管理员!")
                return
            else:
                logger.info(f"用户不在黑名单，正常响应: telegram_id={telegram_id}")
                # bot.answer_callback_query(message.id, "你没有权限执行此操作!")
                # bot.reply_to(message, "你没有权限执行此操作!")
                return func(message, *args, **kwargs)

        return wrapper

    return decorator
