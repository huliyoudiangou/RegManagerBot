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

def confirmation_required(message_text):
    """
    要求用户确认的装饰器

    Args:
        message_text: 提示信息
    """
    def decorator(func):
        @wraps(func)
        def wrapper(message, *args, **kwargs):
            keyboard = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("是", callback_data="confirm_yes"),
                    InlineKeyboardButton("否", callback_data="confirm_no")]
                ]
            )
            bot.reply_to(message, message_text, reply_markup=keyboard)
            
            def callback_handler(call):
              """
              处理按钮点击回调
              """
              if call.data == "confirm_yes":
                  bot.edit_message_text(text=f"已确认：{message_text}", chat_id=call.message.chat.id, message_id=call.message.id)
                  return func(message, *args, **kwargs)
              elif call.data == "confirm_no":
                  bot.edit_message_text(text=f"已取消：{message_text}", chat_id=call.message.chat.id, message_id=call.message.id)
                  logger.debug("用户取消了操作")
                  return
            bot.register_callback_query_handler(callback_handler, func=lambda call: call.data in ["confirm_yes", "confirm_no"])
        return wrapper
    return decorator