# 校验器
from functools import wraps
from app.services.user_service import UserService
from app.services.invite_code_service import InviteCodeService
from app.utils.logger import logger
from app.utils.api_clients import navidrome_api_client
from datetime import datetime
from config import settings
from app.bot.core.bot_instance import bot
# 需要安装的模块：无

def user_exists(service_name):
    """
    验证用户是否存在的装饰器

    Args:
        service_name: 服务名称，例如 "navidrome"
    """
    def decorator(func):
        @wraps(func)
        def wrapper(message, *args, **kwargs):
            telegram_id = message.from_user.id # 修改获取 telegram_id 的方式
            logger.info(f"校验用户是否存在: telegram_id={telegram_id}, service_name={service_name}")

            # 优先在 Web 应用中校验用户是否存在
            if service_name == "navidrome":
                users = navidrome_api_client.get_users()
                if users and users['status'] == 'success':
                    # 遍历查找对应的telegram_id
                    for user_data in users['data']:
                      user = UserService.get_user_by_telegram_id(telegram_id, service_name)
                      if user and user.navidrome_user_id == user_data['id']:
                        # 如果本地数据库中存在，直接返回
                        logger.info(f"用户存在于 Navidrome 和本地数据库: telegram_id={telegram_id}, service_name={service_name}, navidrome_user_id={user_data['id']}")
                        return func(message, *args, **kwargs)
                      elif not user:
                        # 如果本地数据库中不存在，则返回错误信息
                        logger.warning(f"用户不存在于本地数据库，请使用register注册用户: telegram_id={telegram_id}, service_name={service_name}, navidrome_user_id={user_data['id']}")
                        bot.reply_to(message, "用户不存在，请使用/register注册用户")
                        return
                    # 如果 Web 应用中不存在该用户，返回错误信息
                    logger.warning(f"用户不存在于 Navidrome: telegram_id={telegram_id}, service_name={service_name}")
                    bot.reply_to(message, "用户不存在!")
                    return
                else:
                    logger.error(f"获取 Navidrome 用户列表失败: {users}")
                    bot.reply_to(message, "获取用户列表失败，请联系管理员!")
                    return
            else:
                logger.error(f"不支持的服务名称: service_name={service_name}")
                bot.reply_to(message, f"不支持的服务: {service_name}")
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
        logger.info(f"校验用户是否是管理员: telegram_id={telegram_id}")
        if UserService.is_admin(telegram_id):
            logger.info(f"用户是管理员: telegram_id={telegram_id}")
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

        logger.info(f"校验邀请码是否有效: code={code}")
        if not code:
            logger.warning("未提供邀请码")
            bot.reply_to(message, "请提供邀请码!")
            return

        invite_code = InviteCodeService.get_invite_code(code)
        if invite_code and not invite_code.is_used and invite_code.expire_time > datetime.now():
            logger.info(f"邀请码有效: code={code}")
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

            logger.info(f"校验用户积分是否足够: telegram_id={telegram_id}, required_score={required_score}")
            user = UserService.get_user_by_telegram_id(telegram_id, service_name)

            if user and user.score >= required_score:
                logger.info(f"用户积分足够: telegram_id={telegram_id}, score={user.score}, required_score={required_score}")
                return func(message, *args, **kwargs)
            else:
                logger.warning(f"用户积分不足: telegram_id={telegram_id}, score={user.score if user else 0}, required_score={required_score}")
                bot.reply_to(message, "积分不足!")
                return

        return wrapper
    return decorator