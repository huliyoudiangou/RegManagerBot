# 用户命令处理器
import json
from app.services.user_service import UserService
from app.services.score_service import ScoreService
from app.services.invite_code_service import InviteCodeService
from app.utils.message_queue import get_message_queue
from app.utils.logger import logger
from config import settings
from datetime import datetime, timedelta
from app.bot.core.bot_instance import bot
from app.bot.validators import user_exists, confirmation_required, score_enough, chat_type_required
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

message_queue = get_message_queue()


@bot.message_handler(commands=['line'])
@user_exists()
def get_line_command(message):
    """
  处理 /help 命令，输出详细的命令使用说明
  """
    telegram_id = message.from_user.id
    logger.info(f"用户 {telegram_id} 执行了 /line 命令")
    response = '''
        *音海拾贝 Navidrome 服务信息！*
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        🌟服务器地址： （🈲禁网页播放，必ban）
        https://music.makifx.com

        🌟歌词API地址 ： 
        https://lrc.makifx.com/lyrics（可用性未测）

        🌟封面API地址 ： 
        https://lrc.makifx.com/cover（可用性未测）
    '''
    bot.reply_to(message, response, parse_mode="Markdown")


@bot.message_handler(commands=['help'])
@user_exists()
def help_command(message):
    """
  处理 /help 命令，输出详细的命令使用说明
  """
    telegram_id = message.from_user.id
    logger.info(f"用户 {telegram_id} 执行了 /help 命令")
    # response = '''
    #     *音海拾贝 Navidrome 服务信息！*
    #     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #     🌟服务器地址： （🈲禁网页播放，必ban）
    #     https://music.makifx.com

    #     🌟歌词API地址 ： 
    #     https://lrc.makifx.com/lyrics（可用性未测）

    #     🌟封面API地址 ： 
    #     https://lrc.makifx.com/cover（可用性未测）
    # '''
    response = '''
  🎵   *音海拾贝 Navidrome 用户管理机器人* 🤖

        本机器人主要用于管理 Navidrome 用户，并提供积分和邀请码功能。

        📌 *用户命令*
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        🔹 `/register <用户名> <密码>` - 注册用户（邀请码系统关闭时）
        _例如：_ `/register testuser password`

        🔹 `/register <用户名> <密码> <邀请码>` - 使用邀请码注册（邀请码系统开启时）
        _例如：_ `/register testuser password abc123def`

        🔹 `/reg_score_user` - 注册积分用户，用于获取积分购买邀请码

        🔹 `/info` - 查看您的个人信息

        🔹 `/score` - 查看您的积分

        🔹 `/give <Telegram ID> <score>` - 向注册用户赠送积分

        🔹 `/checkin` - 每日签到获得积分

        🔹 `/random_score <红包个数> <积分总数>` - 发送随机积分红包（发送即扣分）

        🔹 `/buyinvite` - 购买邀请码

        🔹 `/bind <用户名> <Navidrome ID>` - 绑定已有服务器账号到 bot 管理

        🔹 `/unbind` - 解绑 Bot 管理（不会删除服务器账号）

        🔹 `/reset_username <new_username>` - 重置服务器用户名

        🔹 `/reset_password <new_password>` - 重置服务器密码

        🔹 `/deleteuser` - 删除您的账户（不可恢复）

        📌 *管理员命令*
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        🔸 `/generate_code [<数量>]` - 生成指定数量的邀请码（默认为 1）
        _例如：_ `/generate_code` 或 `/generate_code 10`

        🔸 `/invite` - 查看所有邀请码

        🔸 `/toggle_invite_code_system` - 开启/关闭邀请码系统

        🔸 `/set_score <telegram_id> <score>` - 设置用户的积分
        _例如：_ `/set_score 12345 100`

        🔸 `/get_score <telegram_id>` 或 `/score <telegram_id>` - 查看用户的积分
        _例如：_ `/get_score 12345` 或 `/score 12345`

        🔸 `/add_score <telegram_id> <score>` - 为用户增加积分
        _例如：_ `/add_score 12345 50`

        🔸 `/reduce_score <telegram_id> <score>` - 减少用户的积分
        _例如：_ `/reduce_score 12345 20`

        🔸 `/set_price <price>` - 设置邀请码的价格
        _例如：_ `/set_price 150`

        🔸 `/stats` - 查看统计信息

        💡 _如需更多帮助，请联系管理员。_
    '''
    bot.reply_to(message, response, parse_mode="Markdown")


@chat_type_required(["group", "supergroup"])
@user_exists(negate=False)
def register_user_command(message):
    if message.text.startswith('/'):
        args = message.text.split()[1:]
    else:
        args = message.text.split()
    if len(args) != 2:
        logger.info(f"参数错误: args={args}")
        bot.reply_to(message, "参数错误，请提供用户名和密码，格式为：用户名 密码")
        return

    username, password = args
    telegram_id = message.from_user.id
    logger.info(f"开始注册用户: telegram_id={telegram_id}, service_type={settings.SERVICE_TYPE}")

    user = UserService.register_user(telegram_id, settings.SERVICE_TYPE, username, password)
    if user:
        logger.info(f"用户注册成功: telegram_id={telegram_id}, user_id={user.id}")
        bot.send_message(message.chat.id, f"注册成功！欢迎 {message.from_user.username} ")
    else:
        logger.error(f"用户注册失败: telegram_id={telegram_id}")
        bot.send_message(message.chat.id, "服务器用户重名了，请重试!")


@chat_type_required(["group", "supergroup"])
# @user_exists(negate=False)
def reg_score_user_command(message):
    """
    处理 /reg_score_user 命令，注册用户
    """
    telegram_id = message.from_user.id
    username = message.from_user.username
    logger.info(f"开始注册用户积分账号: telegram_id={telegram_id}, service_type={settings.SERVICE_TYPE}")

    user = UserService.get_user_by_telegram_id(telegram_id=telegram_id)
    if user:
        logger.info(f"本地用户已存在: user_id={user.id}")
        bot.reply_to(message, f"积分账号已存在，请勿重复注册")
    else:
        # 在本地数据库中创建用户
        user = UserService.register_local_user(telegram_id=telegram_id, username=username)
        user.save()
        logger.info(f"本地用户创建成功: user_id={user.id}")
        bot.reply_to(message, f"本地积分账号注册成功，欢迎您: {username}！")


@chat_type_required(["group", "supergroup"])
@user_exists(negate=True)
@confirmation_required(message_text="你确定要删除该用户吗？")
def delete_user_command(message):
    """
    处理 /deleteuser 命令，删除用户
    """
    telegram_id = message.from_user.id
    service_type = settings.SERVICE_TYPE  # 假设要删除的是 Navidrome 账号

    logger.info(f"用户请求删除账户: telegram_id={telegram_id}, service_type={service_type}")

    # 查找本地数据库中的用户
    user = UserService.get_user_by_telegram_id(telegram_id)
    if user:
        # 调用服务层的删除用户方法
        success = UserService.delete_user(user)
        if success:
            logger.info(
                f"用户删除成功: telegram_id={telegram_id}, service_type={service_type}, username={user.username}")
            bot.reply_to(message, "您的账户已成功删除!")
        else:
            logger.error(
                f"用户删除失败: telegram_id={telegram_id}, service_type={service_type}, username={user.username}")
            bot.reply_to(message, "删除服务器账户失败，本地账户已删除!")
    else:
        logger.warning(f"用户不存在: telegram_id={telegram_id}, service_type={service_type}")
        bot.reply_to(message, "未找到您的账户信息，如已在服务器注册，请使用/bind命令绑定!")


@chat_type_required(["group", "supergroup"])
@user_exists(negate=False)
def use_invite_code_command(message):
    """
    处理 /use_code 命令，用户使用邀请码注册
    """
    telegram_id = message.from_user.id
    # 从消息中提取参数
    if message.text.startswith('/'):
        args = message.text.split()[1:]
    else:
        args = message.text.split()

    if len(args) < 1:
        bot.reply_to(message, "请提供邀请码，格式为：/use_code <[用户名] 邀请码>")
        return

    code = args[-1]

    user = UserService.get_user_by_telegram_id(telegram_id)
    if user and user.invite_code:
        logger.info(f"已使用过邀请码用户注册！")
        bot.send_message(message.chat.id, f"邀请码验证通过，请输入用户名和密码(格式：用户名 密码)：<30s后自动退出>",
                         delay=30)
        bot.register_next_step_handler(message, register_user_command)
        return

        # 验证邀请码的有效性
    invite_code = InviteCodeService.get_invite_code(code)
    if not invite_code:
        bot.reply_to(message, "邀请码无效或已过期！")
        return

    if invite_code.is_used:
        bot.reply_to(message, "邀请码已被使用")
        return

    expire_time = invite_code.create_time + timedelta(days=invite_code.expire_days)
    if expire_time < datetime.now():
        bot.reply_to(message, "邀请码已过期")
        return

    logger.info(f"注册本地用户")
    user = UserService.register_local_user(telegram_id=telegram_id, invite_code=code)
    if user:
        success = InviteCodeService.use_invite_code(code, telegram_id)
        if not success:
            logger.warning(f"邀请码使用失败：{code}")
        else:
            logger.info(f"邀请码成功使用！")
            bot.reply_to(message, f"邀请码验证通过，请输入用户名和密码(格式：用户名 密码)：<30s后自动退出>", delay=30)
            bot.register_next_step_handler(message, register_user_command)
    else:
        logger.warning(f"本地用户注册失败！")
        bot.reply_to(message, "本地用户注册失败！")


@chat_type_required(["group", "supergroup"])
@user_exists(negate=True)
def use_renew_code_command(message):
    """使用续期码 (用户命令)
    格式: /use_renew_code <code>
    示例: /use_renew_code ABC123
    """
    try:
        # 解析参数
        if message.text.startswith('/'):
            args = message.text.split()[1:]
        else:
            args = message.text.split()
        if len(args) < 1:
            bot.reply_to(message, "请提供续期码！")
            return

        code = args[0]  # 续期码
        user_id = message.from_user.id  # 用户 ID

        # 使用续期码
        success = InviteCodeService.use_invite_code(code, user_id, 'renew')
        if success:
            bot.reply_to(message, f"续期码使用成功！您的账户已续期。")
        else:
            bot.reply_to(message, "续期码使用失败，请检查续期码是否正确或是否已过期。")

    except Exception as e:
        logger.error(f"使用续期码失败: {e}")
        bot.reply_to(message, "使用续期码失败，请稍后重试！")


@user_exists(negate=True)
def score_command(message):
    """
    处理 /score 命令，查询用户积分
    """
    telegram_id = message.from_user.id
    service_type = settings.SERVICE_TYPE  # 假设查询的是 Navidrome 账号的积分

    logger.info(f"用户查询积分: telegram_id={telegram_id}, service_type={service_type}")

    # 查找本地数据库中的用户
    user = UserService.get_user_by_telegram_id(telegram_id)
    if user:
        # 调用服务层的获取用户积分方法
        score = ScoreService.get_user_score(user.id)
        if score is not None:
            logger.info(f"用户积分查询成功: telegram_id={telegram_id}, username={user.username}, score={score}")
            bot.reply_to(message, f"您的积分: {score}")
        else:
            logger.error(f"用户积分查询失败: telegram_id={telegram_id}, username={user.username}")
            bot.reply_to(message, "查询积分失败，请重试!")

    else:
        logger.warning(f"用户不存在: telegram_id={telegram_id}, service_type={service_type}")
        bot.reply_to(message, "未找到您的账户信息!")


@user_exists(negate=True)
def checkin_command(message):
    """
    处理 /checkin 命令，用户签到
    """
    telegram_id = message.from_user.id
    service_type = settings.SERVICE_TYPE  # 假设是 Navidrome 账号签到

    logger.info(f"用户请求签到: telegram_id={telegram_id}, service_type={service_type}")

    # 查找本地数据库中的用户
    user = UserService.get_user_by_telegram_id(telegram_id)
    if user:
        # 调用服务层的签到方法
        score = ScoreService.sign_in(user.id)
        if score:
            logger.info(
                f"用户签到成功: telegram_id={telegram_id}, service_type={service_type}, username={user.username}")
            bot.reply_to(message, f"签到成功! 获得了{score}积分!")
        else:
            logger.warning(f"用户签到失败: telegram_id={telegram_id}, service_type={service_type}")
            bot.reply_to(message, "签到失败，您今天已签到!")
    else:
        logger.warning(f"用户不存在: telegram_id={telegram_id}, service_type={service_type}")
        bot.reply_to(message, "未找到您的账户信息!")


@user_exists(negate=True)
@chat_type_required(["group", "supergroup"])
@confirmation_required(f"你确定要购买邀请码嘛？")
def buy_invite_code_command(message):
    """
    处理 /buyinvite 命令，用户购买邀请码
    """
    telegram_id = message.from_user.id
    service_type = settings.SERVICE_TYPE

    logger.info(f"用户请求购买邀请码: telegram_id={telegram_id}, service_type={service_type}")

    # 查找本地数据库中的用户
    user = UserService.get_user_by_telegram_id(telegram_id)
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
                    logger.info(
                        f"用户购买邀请码成功: telegram_id={telegram_id}, service_type={service_type}, code={invite_code.code}, username={user.username}")
                    bot.reply_to(message, f"购买邀请码成功，您的邀请码是：<code>{invite_code.code}</code>，请妥善保管！",
                                 parse_mode='HTML', delay=None)
                else:
                    logger.error(
                        f"用户购买邀请码失败，生成邀请码失败: telegram_id={telegram_id}, service_type={service_type}, username={user.username}")
                    bot.reply_to(message, "购买邀请码失败，生成邀请码失败，请重试！")
            else:
                logger.error(
                    f"用户购买邀请码失败，扣除积分失败: telegram_id={telegram_id}, service_type={service_type}, username={user.username}")
                bot.reply_to(message, "购买邀请码失败，扣除积分失败，请重试！")
        else:
            logger.warning(
                f"用户购买邀请码失败，积分不足: telegram_id={telegram_id}, service_type={service_type}, username={user.username}")
            bot.reply_to(message, f"购买邀请码失败，您的积分不足，邀请码需要 {required_score} 积分！")
    else:
        logger.warning(f"用户不存在: telegram_id={telegram_id}, service_type={service_type}")
        bot.reply_to(message, "未找到您的账户信息!")


@chat_type_required(["group", "supergroup"])
@user_exists(negate=True)
def info_command(message):
    """
    处理 /info 命令，用户信息查询
    """
    telegram_id = message.from_user.id
    user = UserService.get_user_by_telegram_id(telegram_id)
    if user:
        logger.info(f"user: {user}")
        logger.info(f"用户信息查询成功: telegram_id={telegram_id}, user_id={user.id}")
        response = f"您的信息如下：\n" \
                   f"Telegram ID: {user.telegram_id}\n" \
                   f"用户名: {user.username}\n" \
                   f"积分: {user.score}\n" \
                   f"状态: {user.status}\n" \
                   f"过期时间: {user.expiration_date}\n" \
                   f"本地数据库ID: {user.id}\n" \
                   f"服务器用户ID: {user.service_user_id}"
        bot.reply_to(message, response)
    else:
        logger.error(f"用户信息查询失败: telegram_id={telegram_id}")
        bot.reply_to(message, "未注册用户，请先注册！")


@chat_type_required(["group", "supergroup"])
@user_exists(negate=True)
@confirmation_required(f"你确定要赠送积分嘛？")
def give_score_command(message):
    """
    处理 /give 命令，用户赠送积分
     /give <telegram_id> <score>
    """
    telegram_id = message.from_user.id
    service_type = settings.SERVICE_TYPE

    logger.info(f"用户请求赠送积分: telegram_id={telegram_id}, service_type={service_type}")

    if message.text.startswith('/'):
        args = message.text.split()[1:]
    else:
        args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "参数错误，请提供接收者 Telegram ID 和积分数，格式为：/give <telegram_id> <score>")
        return

    try:
        receiver_telegram_id, score = args
        receiver_telegram_id = int(receiver_telegram_id)
        score = int(score)
    except ValueError:
        bot.reply_to(message, "参数错误，接收者 Telegram ID 和积分数必须是整数！")
        return

    if telegram_id == receiver_telegram_id:
        bot.reply_to(message, "不能给自己赠送积分！")
        return

    # 检查赠送者是否存在
    sender = UserService.get_user_by_telegram_id(telegram_id)
    if not sender:
        bot.reply_to(message, "未找到您的账户信息!")
        return

    # 检查接收者是否存在
    receiver = UserService.get_user_by_telegram_id(receiver_telegram_id, service_type)
    if not receiver:
        bot.reply_to(message, f"未找到接收者 {receiver_telegram_id} 的账户信息！")
        return

    # 检查赠送者积分是否足够
    if sender.score < score:
        bot.reply_to(message, f"您的积分不足，无法赠送 {score} 积分！")
        return

    # 扣除赠送者积分，增加接收者积分
    sender = ScoreService.reduce_score(sender.id, score)
    receiver = ScoreService.add_score(receiver.id, score)

    if sender and receiver:
        logger.info(f"用户赠送积分成功: sender_id={sender.id}, receiver_id={receiver.id}, score={score}")
        bot.reply_to(message, f"您已成功向用户 {receiver_telegram_id} 赠送 {score} 积分!")
    else:
        logger.error(f"用户赠送积分失败: sender_id={sender.id}, receiver_id={receiver.id}, score={score}")
        bot.reply_to(message, f"积分赠送失败，请重试!")


@chat_type_required(["group", "supergroup"])
def bind_command(message):
    """
    处理 /bind 命令，绑定 Web 服务账户
    /bind <username> <password>
    """
    telegram_id = message.from_user.id
    service_type = settings.SERVICE_TYPE

    logger.info(f"用户请求绑定账户: telegram_id={telegram_id}, service_type={service_type}")

    if message.text.startswith('/'):
        args = message.text.split()[1:]
    else:
        args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "参数错误，请提供用户名和用户密码，格式为：/bind <username> <password>")
        return

    username, password = args

    # 验证用户
    user_id = UserService.auth_user_by_username_and_password(username, password)
    if user_id:
        user = UserService.get_user_by_service_user_id(user_id)
        if user:
            logger.info(f"{telegram_id}请求换绑TG！")
            u = UserService.update_user_telegram_id(user, telegram_id)
            if u:
                bot.reply_to(message, "Telegram 换绑成功")
                logger.info(f"用户换绑成功：telegram_id={telegram_id}")
            else:
                bot.reply_to(message, "Telegram 换绑失败！")
                logger.error(f"用户换绑失败：telegram_id={telegram_id}")
        else:    
            logger.info(
                f"用户绑定账户成功: telegram_id={telegram_id}, service_type={service_type}, username={username}, user_id={user_id}")
            user = UserService.register_local_user(telegram_id=telegram_id, service_type=service_type,
                                                service_user_id=user_id, username=username)
            bot.reply_to(message, "账户绑定成功!")
    else:
        logger.error(
            f"用户绑定账户失败: telegram_id={telegram_id}, service_type={service_type}, username={username}, user_id={user_id}")
        bot.reply_to(message, "账户绑定失败，请重试!")


@chat_type_required(["group", "supergroup"])
@user_exists(negate=True)
def unbind_command(message):
    """
    处理 /unbind 命令，解绑 Web 服务账户并删除本地用户
    """
    telegram_id = message.from_user.id
    service_type = settings.SERVICE_TYPE

    logger.info(f"用户请求解绑账户: telegram_id={telegram_id}, service_type={service_type}")

    # 查找本地数据库中的用户
    user = UserService.get_user_by_telegram_id(telegram_id)
    if user:
        # 删除本地用户
        UserService.delete_user(user)
        logger.info(f"用户解绑成功: telegram_id={telegram_id}, service_type={service_type}")
        bot.reply_to(message, "解绑成功！已删除您的本地账户信息。")
    else:
        logger.warning(f"用户不存在: telegram_id={telegram_id}, service_type={service_type}")
        bot.reply_to(message, "未找到您的账户信息！")


@chat_type_required(["group", "supergroup"])
@user_exists(negate=True)
@confirmation_required(f"你确定要重置密码嘛？")
def reset_password_command(message):
    """
    处理 /reset_password 命令，重置密码
    """
    telegram_id = message.from_user.id
    service_type = settings.SERVICE_TYPE

    logger.info(f"用户请求重置密码: telegram_id={telegram_id}, service_type={service_type}")

    if message.text.startswith('/'):
        args = message.text.split()[1:]
    else:
        args = message.text.split()
    if len(args) != 1:
        bot.reply_to(message, "参数错误，请提供新密码，格式为：/reset_password <new_password>")
        return

    new_password = args[0]
    user = UserService.get_user_by_telegram_id(telegram_id)
    if user and UserService.get_info_in_service_by_user_id(user.service_user_id):
        # 重置密码
        result = UserService.reset_password(user, new_password=new_password)
        if result:
            logger.info(f"用户重置密码成功: telegram_id={telegram_id}, service_type={service_type}")
            bot.reply_to(message, "密码重置成功！")
        else:
            logger.warning(f"用户不存在: telegram_id={telegram_id}, service_type={service_type}")
            bot.reply_to(message, "密码重置失败，请联系管理员！")

    else:
        logger.warning(f"用户不存在: telegram_id={telegram_id}, service_type={service_type}")
        bot.reply_to(message, "该用户未注册！")


@chat_type_required(["group", "supergroup"])
@user_exists(negate=True)
def reset_username_command(message):
    """
    处理 /reset_username 命令，重置用户名
    """
    telegram_id = message.from_user.id
    service_type = settings.SERVICE_TYPE

    logger.info(f"用户请求重置用户名: telegram_id={telegram_id}, service_type={service_type}")

    if message.text.startswith('/'):
        args = message.text.split()[1:]
    else:
        args = message.text.split()
    if len(args) != 1:
        bot.reply_to(message, "参数错误，请提供新用户名，格式为：/reset_username <new_username>")
        return

    new_username = args[0]
    user = UserService.get_user_by_telegram_id(telegram_id)
    if user and user.username != new_username:
        if UserService.get_info_in_service_by_user_id(user.service_user_id):
            # 重置用户名
            result = UserService.reset_username(user, new_username=new_username)
            if result:
                UserService.update_user_name(user, new_username)
                logger.info(f"用户重置用户名成功: telegram_id={telegram_id}, service_type={service_type}")
                bot.reply_to(message, f"用户名重置成功，请使用{new_username}登录！")
            else:
                logger.warning(f"服务器出错: telegram_id={telegram_id}, service_type={service_type}")
                bot.reply_to(message, "服务器出错，请联系管理员！")
        else:
            logger.warning(f"服务器无该用户: telegram_id={telegram_id}, service_type={service_type}")
            bot.reply_to(message, "服务器找不到该用户！")
    else:
        logger.warning(f"用户重名: telegram_id={telegram_id}, service_type={service_type}")
        bot.reply_to(message, "用户重名，请重新选择用户名！")


@chat_type_required(["private"])
@user_exists(negate=True)
@score_enough()
@confirmation_required(f"你确定要发随机红包嘛？")
def random_score_command(message):
    """发送带有按钮的菜单"""
    bot.delete_message(message.chat.id, message.message_id)
    username = message.from_user.username
    if message.text.startswith('/'):
        args = message.text.split()[1:]
    else:
        args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "参数错误，请提供参数，格式为：/random_score <participants_count> <total_score>")
        return
    try:
        participants_count = int(args[0])
        total_score = int(args[1])
    except ValueError:
        bot.reply_to(message, "参数错误，参与人数和总积分数必须是整数！")

        return
    event_id = ScoreService.create_random_score_event(create_user_id=message.from_user.id,
                                                      telegram_chat_id=message.chat.id, total_score=total_score,
                                                      participants_count=participants_count)
    if not event_id:
        bot.reply_to(message, "创建积分活动失败")

        return

    user = UserService.get_user_by_telegram_id(message.from_user.id)
    logger.info(
        f"用户 {user.username} 发送了总分为{total_score}分随机积分红包，原有积分为{user.score}分, 剩余积分为{user.score - total_score}分")
    if ScoreService.reduce_score(user.id, total_score):
        logger.info(f"积分成功扣除{total_score}分")

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("点击抽积分", callback_data=f"random_score_{event_id}")]
        ]
    )
    msg = f'''
            🧧 *随机积分红包来了~*
            _感谢 {username} 发的随机积分红包！_
          '''
    bot.send_message(message.chat.id, msg, reply_markup=keyboard, parse_mode="Markdown", disable_web_page_preview=True,
                     delay=None)


@bot.callback_query_handler(func=lambda call: call.data.startswith("random_score_"))
def handle_random_score_callback(call):
    """处理随机积分的按钮点击事件"""
    event_id = int(call.data.split("_")[2])
    user_id = call.from_user.id
    user_name = call.from_user.username if call.from_user.username else call.from_user.first_name  # 优先获取用户名，如果没有就获取first_name

    user = UserService.get_user_by_telegram_id(user_id)
    if not user:
        bot.send_message(call.message.chat.id,
                         f"未注册用户[{user_name}](https://t.me/{user_name})，请使用`/reg_score_user`注册积分账号。",
                         parse_mode="Markdown", disable_web_page_preview=True)
        logger.info(f"未注册用户{user_name}")

        return

    score = ScoreService.use_random_score(event_id=event_id, user_id=user_id, user_name=user_name)
    if score:
        bot.send_message(call.message.chat.id, f"恭喜您：[{user_name}](https://t.me/{user_name})，获得{score}积分！",
                         parse_mode="Markdown", disable_web_page_preview=True)
        event_data = ScoreService.get_random_score_event(event_id)
        if event_data and event_data['is_finished']:
            score_result = json.loads(event_data['score_result'])
            response = f"*积分分发完毕, 中奖信息如下*\n"
            response += f"-----------------------\n"
            for item in score_result:
                response += f"用户: [{item['user_name']}](https://t.me/{item['user_name']})，获取积分： {item['score']}分\n"
            logger.info(f"chat: {call.message.chat.id}, message_id: {call.message.message_id}")
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"{response}",
                                  parse_mode="Markdown", disable_web_page_preview=True, delay=30)

    elif score == 0:
        bot.send_message(call.message.chat.id, f"积分已经分发完毕")
    else:
        bot.send_message(call.message.chat.id,
                         f"[{user_name}](https://t.me/{user_name})您已经获取过奖励, 请勿重复点击！",
                         parse_mode="Markdown", disable_web_page_preview=True)
