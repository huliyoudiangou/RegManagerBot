# 管理员命令处理器
import telebot
from app.bot.validators import admin_required
from app.services.user_service import UserService
from app.services.score_service import ScoreService
from app.services.invite_code_service import InviteCodeService
from app.utils.logger import logger
from config import settings
from app.bot.core.bot_instance import bot

# 需要安装的模块：无


@bot.message_handler(commands=['generate_code'])
@admin_required
def generate_invite_code_command(message):
    """生成邀请码 (管理员命令)"""
    telegram_id = message.from_user.id
    invite_code = InviteCodeService.generate_invite_code(telegram_id)
    if invite_code:
        bot.reply_to(message, f"邀请码已生成：{invite_code.code}")
    else:
        bot.reply_to(message, "邀请码生成失败，请重试！")

@bot.message_handler(commands=['invite'])
@admin_required
def get_all_invite_codes_command(message):
    """查看所有邀请码 (管理员命令)"""
    invite_codes = InviteCodeService.get_all_invite_codes()
    if invite_codes:
      response = "邀请码列表：\n"
      for invite_code in invite_codes:
        response += f"ID: {invite_code.id}, 邀请码: {invite_code.code}, 是否已使用: {'是' if invite_code.is_used else '否'}, 创建时间: {invite_code.create_time}, 过期时间: {invite_code.expire_time}, 创建者ID: {invite_code.create_user_id}\n"
      bot.reply_to(message, response)
    else:
      bot.reply_to(message, "获取邀请码列表失败，请重试！")

@bot.message_handler(commands=['toggle_invite_code_system'])
@admin_required
def toggle_invite_code_system_command(message):
    """开启/关闭邀请码系统 (管理员命令)"""
    settings.INVITE_CODE_SYSTEM_ENABLED = not settings.INVITE_CODE_SYSTEM_ENABLED
    logger.info(f"邀请码系统状态已更改: {settings.INVITE_CODE_SYSTEM_ENABLED}")
    bot.reply_to(message, f"邀请码系统已{'开启' if settings.INVITE_CODE_SYSTEM_ENABLED else '关闭'}")

@bot.message_handler(commands=['set_score'])
@admin_required
def set_score_command(message):
    """
    设置用户积分 (管理员命令)
    /set_score <telegram_id> <score>
    """
    telegram_id = message.from_user.id
    service_name = "navidrome"

    logger.info(f"管理员设置用户积分: telegram_id={telegram_id}, service_name={service_name}")

    args = message.text.split()[1:]
    if len(args) != 2:
        bot.reply_to(message, "参数错误，请提供用户 Telegram ID 和积分数，格式为：/set_score <telegram_id> <score>")
        return

    try:
        target_telegram_id, score = args
        target_telegram_id = int(target_telegram_id)
        score = int(score)
    except ValueError:
        bot.reply_to(message, "参数错误，用户 Telegram ID 和积分数必须是整数！")
        return

    # 查找本地数据库中的用户
    user = UserService.get_user_by_telegram_id(target_telegram_id, service_name)
    if user:
        # 调用服务层的设置用户积分方法
        user = ScoreService.update_user_score(user.id, score)
        if user:
            logger.info(f"用户积分设置成功: user_id={user.id}, score={user.score}")
            bot.reply_to(message, f"用户 {target_telegram_id} 的积分已设置为: {score}")
        else:
            logger.error(f"用户积分设置失败: telegram_id={target_telegram_id}")
            bot.reply_to(message, "设置积分失败，请重试！")
    else:
        logger.warning(f"用户不存在: telegram_id={target_telegram_id}, service_name={service_name}")
        bot.reply_to(message, f"未找到用户: {target_telegram_id}")

@bot.message_handler(commands=['get_score', 'score'])
@admin_required
def get_score_command(message):
    """
    查看用户积分 (管理员命令)
    /score <telegram_id>
    """
    telegram_id = message.from_user.id
    service_name = "navidrome"

    logger.info(f"管理员查看用户积分: telegram_id={telegram_id}, service_name={service_name}")

    args = message.text.split()[1:]
    if len(args) != 1:
        bot.reply_to(message, "参数错误，请提供用户 Telegram ID，格式为：/score <telegram_id>")
        return

    try:
        target_telegram_id = int(args[0])
    except ValueError:
        bot.reply_to(message, "参数错误，用户 Telegram ID 必须是整数！")
        return

    # 查找本地数据库中的用户
    user = UserService.get_user_by_telegram_id(target_telegram_id, service_name)
    if user:
        # 调用服务层的获取用户积分方法
        score = ScoreService.get_user_score(user.id)
        if score is not None:
            logger.info(f"用户积分查询成功: telegram_id={target_telegram_id}, score={score}")
            bot.reply_to(message, f"用户 {target_telegram_id} 的积分: {score}")
        else:
            logger.error(f"用户积分查询失败: telegram_id={target_telegram_id}")
            bot.reply_to(message, "查询积分失败，请重试！")
    else:
        logger.warning(f"用户不存在: telegram_id={target_telegram_id}, service_name={service_name}")
        bot.reply_to(message, f"未找到用户: {target_telegram_id}")

@bot.message_handler(commands=['add_score'])
@admin_required
def add_score_command(message):
    """
    增加用户积分 (管理员命令)
    /add_score <telegram_id> <score>
    """
    telegram_id = message.from_user.id
    service_name = "navidrome"

    logger.info(f"管理员增加用户积分: telegram_id={telegram_id}, service_name={service_name}")

    args = message.text.split()[1:]
    if len(args) != 2:
        bot.reply_to(message, "参数错误，请提供用户 Telegram ID 和积分数，格式为：/add_score <telegram_id> <score>")
        return

    try:
        target_telegram_id, score = args
        target_telegram_id = int(target_telegram_id)
        score = int(score)
    except ValueError:
        bot.reply_to(message, "参数错误，用户 Telegram ID 和积分数必须是整数！")
        return

    # 查找本地数据库中的用户
    user = UserService.get_user_by_telegram_id(target_telegram_id, service_name)
    if user:
        # 调用服务层的增加用户积分方法
        user = ScoreService.add_score(user.id, score)
        if user:
            logger.info(f"用户积分增加成功: user_id={user.id}, score={user.score}")
            bot.reply_to(message, f"已为用户 {target_telegram_id} 增加积分: {score}")
        else:
            logger.error(f"用户积分增加失败: telegram_id={target_telegram_id}")
            bot.reply_to(message, "增加积分失败，请重试！")
    else:
        logger.warning(f"用户不存在: telegram_id={target_telegram_id}, service_name={service_name}")
        bot.reply_to(message, f"未找到用户: {target_telegram_id}")

@bot.message_handler(commands=['reduce_score'])
@admin_required
def reduce_score_command(message):
    """
    减少用户积分 (管理员命令)
    /reduce_score <telegram_id> <score>
    """
    telegram_id = message.from_user.id
    service_name = "navidrome"

    logger.info(f"管理员减少用户积分: telegram_id={telegram_id}, service_name={service_name}")

    args = message.text.split()[1:]
    if len(args) != 2:
        bot.reply_to(message, "参数错误，请提供用户 Telegram ID 和积分数，格式为：/reduce_score <telegram_id> <score>")
        return

    try:
        target_telegram_id, score = args
        target_telegram_id = int(target_telegram_id)
        score = int(score)
    except ValueError:
        bot.reply_to(message, "参数错误，用户 Telegram ID 和积分数必须是整数！")
        return

    # 查找本地数据库中的用户
    user = UserService.get_user_by_telegram_id(target_telegram_id, service_name)
    if user:
        # 调用服务层的减少用户积分方法
        user = ScoreService.reduce_score(user.id, score)
        if user:
            logger.info(f"用户积分减少成功: user_id={user.id}, score={user.score}")
            bot.reply_to(message, f"已为用户 {target_telegram_id} 减少积分: {score}")
        else:
            logger.error(f"用户积分减少失败: telegram_id={target_telegram_id}")
            bot.reply_to(message, "减少积分失败，请重试！")
    else:
        logger.warning(f"用户不存在: telegram_id={target_telegram_id}, service_name={service_name}")
        bot.reply_to(message, f"未找到用户: {target_telegram_id}")

