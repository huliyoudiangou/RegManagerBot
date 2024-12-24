# 用户命令处理器
import telebot
from app.services.user_service import UserService
from app.services.score_service import ScoreService
from app.services.invite_code_service import InviteCodeService
from app.bot.validators import user_exists
from app.utils.logger import logger
from config import settings
from datetime import datetime
from app.bot.core.bot_instance import bot

# 需要安装的模块：无

@bot.message_handler(commands=['register'])
@user_exists(service_name="navidrome")
def register_command(message):
    """
    处理 /register 命令，用户注册

    支持以下几种注册方式：
    1. 管理员注册：/register <用户名> <密码>
    2. 邀请码系统开启：/register <用户名> <密码> <邀请码>
    3. 邀请码系统关闭：/register <用户名> <密码> <任意邀请码> (为了统一格式，可以随意填写邀请码，但不使用)
    """
    telegram_id = message.from_user.id
    user = UserService.get_user_by_telegram_id(telegram_id, "navidrome")

    # 只有当用户不存在于 Web 应用时才需要注册
    if user and user.navidrome_user_id:
        bot.reply_to(message, "您已经注册过了!")
        return

    args = message.text.split()[1:]
    logger.info(f"args: {args}")
    # 管理员注册
    if UserService.is_admin(telegram_id):
        if len(args) != 2:
            bot.reply_to(message, "管理员注册，请提供用户名和密码，格式为：/register <用户名> <密码>")
            return
        username, password = args
        logger.info(f"username: {username}")
        logger.info(f"passwd: {password}")
        # 调用 UserService.register_user 方法注册用户
        user = UserService.register_user(telegram_id, "navidrome", username, password)
        if user:
            logger.info(f"管理员注册成功: telegram_id={telegram_id}, user_id={user.id}")
            bot.reply_to(message, "管理员注册成功!")
        else:
            logger.error(f"管理员注册失败: telegram_id={telegram_id}")
            bot.reply_to(message, "管理员注册失败，请重试!")
        return

    # 邀请码系统开启
    if settings.INVITE_CODE_SYSTEM_ENABLED:
        if len(args) != 3:
            bot.reply_to(message, "邀请码系统已开启，请提供用户名、密码和邀请码，格式为：/register <用户名> <密码> <邀请码>")
            return
        username, password, code = args
        # 验证邀请码
        invite_code = InviteCodeService.get_invite_code(code)
        if not invite_code:
            bot.reply_to(message, "邀请码无效！")
            return

        if invite_code.is_used:
          bot.reply_to(message, "邀请码已被使用！")
          return

        if invite_code.expire_time < datetime.now():
          bot.reply_to(message, "邀请码已过期！")
          return
          
        # 使用邀请码
        success = InviteCodeService.use_invite_code(code, telegram_id)
        if not success:
            bot.reply_to(message, "邀请码使用失败！")
            return

        # 注册用户
        user = UserService.register_user(telegram_id, "navidrome", username, password)
        if user:
            logger.info(f"用户使用邀请码注册成功: telegram_id={telegram_id}, user_id={user.id}, code={code}")
            bot.reply_to(message, "注册成功!")
        else:
            logger.error(f"用户使用邀请码注册失败: telegram_id={telegram_id}, code={code}")
            bot.reply_to(message, "注册失败，请重试!")
        return

    # 邀请码系统关闭
    else:
        if len(args) < 2:
            bot.reply_to(message, "邀请码系统已关闭，请提供用户名和密码，格式为：/register <用户名> <密码> [邀请码]")
            return
        username, password = args[:2]  # 只取前两个参数作为用户名和密码
        # 调用 UserService.register_user 方法注册用户
        user = UserService.register_user(telegram_id, "navidrome", username, password)
        if user:
            logger.info(f"用户注册成功: telegram_id={telegram_id}, user_id={user.id}")
            bot.reply_to(message, "注册成功!")
        else:
            logger.error(f"用户注册失败: telegram_id={telegram_id}")
            bot.reply_to(message, "注册失败，请重试!")
        return

@bot.message_handler(commands=['deleteuser'])
def delete_user_command(message):
    """
    处理 /deleteuser 命令，删除用户
    """
    telegram_id = message.from_user.id
    service_name = "navidrome"  # 假设要删除的是 Navidrome 账号

    logger.info(f"用户请求删除账户: telegram_id={telegram_id}, service_name={service_name}")

    # 查找本地数据库中的用户
    user = UserService.get_user_by_telegram_id(telegram_id, service_name)
    logger.info(f"user: {user}")
    if user:
        # 调用服务层的删除用户方法
        success = UserService.delete_user(user)
        if success:
            logger.info(f"用户删除成功: telegram_id={telegram_id}, service_name={service_name}")
            bot.reply_to(message, "您的账户已成功删除!")
        else:
            logger.error(f"用户删除失败: telegram_id={telegram_id}, service_name={service_name}")
            bot.reply_to(message, "删除账户失败，请重试!")
    else:
        logger.warning(f"用户不存在: telegram_id={telegram_id}, service_name={service_name}")
        bot.reply_to(message, "未找到您的账户信息!")

@bot.message_handler(commands=['score'])
def score_command(message):
    """
    处理 /score 命令，查询用户积分
    """
    telegram_id = message.from_user.id
    service_name = "navidrome"  # 假设查询的是 Navidrome 账号的积分

    logger.info(f"用户查询积分: telegram_id={telegram_id}, service_name={service_name}")

    # 查找本地数据库中的用户
    user = UserService.get_user_by_telegram_id(telegram_id, service_name)
    if user:
        # 调用服务层的获取用户积分方法
        score = ScoreService.get_user_score(user.id)
        if score is not None:
            logger.info(f"用户积分查询成功: telegram_id={telegram_id}, score={score}")
            bot.reply_to(message, f"您的积分: {score}")
        else:
            logger.error(f"用户积分查询失败: telegram_id={telegram_id}")
            bot.reply_to(message, "查询积分失败，请重试!")
    else:
        logger.warning(f"用户不存在: telegram_id={telegram_id}, service_name={service_name}")
        bot.reply_to(message, "未找到您的账户信息!")

@bot.message_handler(commands=['checkin'])
def checkin_command(message):
    """
    处理 /checkin 命令，用户签到
    """
    telegram_id = message.from_user.id
    service_name = "navidrome"  # 假设是 Navidrome 账号签到

    logger.info(f"用户请求签到: telegram_id={telegram_id}, service_name={service_name}")

    # 查找本地数据库中的用户
    user = UserService.get_user_by_telegram_id(telegram_id, service_name)
    if user:
        # 调用服务层的签到方法
        success = ScoreService.sign_in(user.id)
        if success:
            logger.info(f"用户签到成功: telegram_id={telegram_id}, service_name={service_name}")
            bot.reply_to(message, "签到成功!")
        else:
            logger.warning(f"用户签到失败: telegram_id={telegram_id}, service_name={service_name}")
            bot.reply_to(message, "签到失败，您今天已签到!")
    else:
        logger.warning(f"用户不存在: telegram_id={telegram_id}, service_name={service_name}")
        bot.reply_to(message, "未找到您的账户信息!")

@bot.message_handler(commands=['buyinvite'])
def buy_invite_code_command(message):
    """
    处理 /buyinvite 命令，用户购买邀请码
    """
    telegram_id = message.from_user.id
    service_name = "navidrome"

    logger.info(f"用户请求购买邀请码: telegram_id={telegram_id}, service_name={service_name}")

    # 查找本地数据库中的用户
    user = UserService.get_user_by_telegram_id(telegram_id, service_name)
    if user:
        # 从配置文件中获取购买邀请码所需积分
        required_score = settings.INVITE_CODE_PRICE
        if user.score >= required_score:
            # 扣除积分
            success = ScoreService.reduce_score(user.id, required_score)
            if success:
                # 生成邀请码
                invite_code = InviteCodeService.generate_invite_code(telegram_id)
                if invite_code:
                    logger.info(f"用户购买邀请码成功: telegram_id={telegram_id}, service_name={service_name}, code={invite_code.code}")
                    bot.reply_to(message, f"购买邀请码成功，您的邀请码是：{invite_code.code}，请妥善保管！")
                else:
                    logger.error(f"用户购买邀请码失败，生成邀请码失败: telegram_id={telegram_id}, service_name={service_name}")
                    bot.reply_to(message, "购买邀请码失败，生成邀请码失败，请重试！")
            else:
                logger.error(f"用户购买邀请码失败，扣除积分失败: telegram_id={telegram_id}, service_name={service_name}")
                bot.reply_to(message, "购买邀请码失败，扣除积分失败，请重试！")
        else:
            logger.warning(f"用户购买邀请码失败，积分不足: telegram_id={telegram_id}, service_name={service_name}")
            bot.reply_to(message, f"购买邀请码失败，您的积分不足，邀请码需要 {required_score} 积分！")
    else:
        logger.warning(f"用户不存在: telegram_id={telegram_id}, service_name={service_name}")
        bot.reply_to(message, "未找到您的账户信息!")