# 用户命令处理器
import json
from app.services.user_service import UserService
from app.services.score_service import ScoreService
from app.services.invite_code_service import InviteCodeService
from app.utils.logger import logger 
from app.utils.utils import paginate_list, get_username_by_telegram_id
from config import settings
from datetime import datetime
from app.bot.core.bot_instance import bot
from app.bot.validators import user_exists, confirmation_required
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# 需要安装的模块：无
@bot.message_handler(commands=['start'])
def start_command(message):
    """
    处理 /start 命令
    """
    telegram_id = message.from_user.id
    logger.info(f"用户 {telegram_id} 执行了 /start 命令")
    response = "欢迎使用注册机器人！祝您每天开心！\n\n" \
               "本机器人主要用于管理 Navidrome 用户，并提供积分和邀请码功能。\n" \
               "您可以通过以下命令进行注册和管理：\n" \
               "- `/register <用户名> <密码>`: 注册用户 (邀请码系统关闭时)\n" \
               "- `/register <用户名> <密码> <邀请码>`: 使用邀请码注册用户 (邀请码系统开启时)\n" \
               "- `/info`: 查看您的个人信息\n" \
               "- `/score`: 查看您的积分\n" \
               "- `/checkin`: 每日签到获得积分\n" \
               "- `/buyinvite`: 购买邀请码\n" \
               "- `/reset_password`: 重置密码\n" \
               "- `/reset_username`: 重置登录用户名\n" \
               "- `/deleteuser`: 删除您的账户!!!\n" \
               "- `/bind`: 绑定您的账户\n" \
               "- `/unbind`: 解绑您的账户\n" \
               "\n您可以使用 `/help` 命令获取更详细的帮助信息。"
    bot.reply_to(message, response)

@bot.message_handler(commands=['help'])
def help_command(message):
  """
  处理 /help 命令，输出详细的命令使用说明
  """
  telegram_id = message.from_user.id
  logger.info(f"用户 {telegram_id} 执行了 /help 命令")
  response = "本机器人主要用于管理 Navidrome 用户，并提供积分和邀请码功能。\n\n" \
             "**用户命令：**\n" \
             "- `/register <用户名> <密码>`: 注册用户 (邀请码系统关闭时)。\n" \
             "   -  示例: `/register testuser password` \n" \
            "- `/register <用户名> <密码> <邀请码>`: 使用邀请码注册用户(邀请码系统开启时)\n"\
             "   -  示例: `/register testuser password abc123def` \n" \
             "- `/info`: 查看您的个人信息。\n" \
             "   -  示例: `/info` \n" \
             "- `/score`: 查看您的积分。\n" \
             "   -  示例: `/score` \n" \
             "- `/checkin`: 每日签到获得积分。\n" \
             "   -  示例: `/checkin` \n" \
             "- `/buyinvite`: 购买邀请码。\n" \
             "   -  示例: `/buyinvite` \n" \
            "- `/deleteuser`: 删除您的账户。\n" \
             "   -  示例: `/deleteuser` \n" \
             "\n**管理员命令：**\n" \
             "- `/generate_code [<数量>]`：生成指定数量的邀请码（默认为 1）。\n" \
             "   -  示例: `/generate_code` 或 `/generate_code 10`\n" \
             "- `/invite`：查看所有邀请码。\n" \
             "   -  示例: `/invite` \n" \
             "- `/toggle_invite_code_system`：开启/关闭邀请码系统。\n" \
             "   -  示例: `/toggle_invite_code_system`\n" \
             "- `/set_score <telegram_id> <score>`：设置用户的积分。\n" \
             "   -  示例: `/set_score 12345 100` \n" \
              "- `/get_score <telegram_id>` 或 `/score <telegram_id>`：查看用户的积分。\n" \
             "   -  示例: `/get_score 12345` 或 `/score 12345` \n" \
             "- `/add_score <telegram_id> <score>`：为用户增加积分。\n" \
             "   -  示例: `/add_score 12345 50` \n" \
              "- `/reduce_score <telegram_id> <score>`：减少用户的积分。\n" \
             "   -  示例: `/reduce_score 12345 20`\n" \
            "- `/set_price <price>`: 设置邀请码的价格。\n" \
             "   -  示例: `/set_price 150`\n" \
            "- `/stats`: 查看统计信息。\n" \
             "   -  示例: `/stats` \n"

  bot.reply_to(message, response)

@bot.message_handler(commands=['register'])
@user_exists("navidrome", negate=True)
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
    # if user and user.navidrome_user_id:
    #     bot.reply_to(message, "您已经注册过了, 如想重新注册，请先执行/deleteuser删除本地用户再注册!")
    #     return

    args = message.text.split()[1:]
    # 管理员注册
    if UserService.is_admin(telegram_id):
        if len(args) != 2:
            bot.reply_to(message, "管理员注册，请提供用户名和密码，格式为：/register <用户名> <密码>")
            return
        username, password = args
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

        # 注册用户
        user = UserService.register_user(telegram_id, "navidrome", username, password, code=code)
        if user:
            logger.info(f"用户使用邀请码注册成功: telegram_id={telegram_id}, username={username}, code={code}")
            bot.reply_to(message, f"使用邀请码{code}注册成功!")
            
            # 使用邀请码
            success = InviteCodeService.use_invite_code(code, telegram_id)
            if not success:
                bot.reply_to(message, "邀请码使用失败！")
                return
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
            logger.info(f"用户注册成功: telegram_id={telegram_id}, username={username}")
            bot.reply_to(message, "注册成功!")
        else:
            logger.error(f"用户注册失败: telegram_id={telegram_id}")
            bot.reply_to(message, "注册失败，请重试!")
        return

@bot.message_handler(commands=['reg_score_user'])
def reg_score_user_command(message):
    """
    处理 /reg_score_user 命令，注册用户
    """
    telegram_id = message.from_user.id
    username = message.from_user.username
    service_name = "navidrome"
    logger.info(f"开始注册用户积分账号: telegram_id={telegram_id}, service_name={service_name}")

    # 检查用户是否已存在
    user = UserService.get_user_by_telegram_id(telegram_id, service_name)
    if user:
        bot.reply_to(message, "您已经注册过了，请使用 /info 命令查看您的信息。")
        logger.warning(f"用户已存在: telegram_id={telegram_id}, service_name={service_name}")
        return

    # 在本地数据库中创建用户
    user = UserService.register_local_user(telegram_id=telegram_id, service_name=service_name, username=username)
    user.save()
    logger.info(f"本地用户创建成功: user_id={user.id}")
    bot.reply_to(message, f"本地积分账号注册成功，欢迎您: {username}！")
    
@bot.message_handler(commands=['deleteuser'])
@user_exists(service_name="navidrome")
@confirmation_required(message_text="你确定要删除该用户吗？")
def delete_user_command(message):
    """
    处理 /deleteuser 命令，删除用户
    """
    telegram_id = message.from_user.id
    service_name = "navidrome"  # 假设要删除的是 Navidrome 账号

    logger.info(f"用户请求删除账户: telegram_id={telegram_id}, service_name={service_name}")

    # 查找本地数据库中的用户
    user = UserService.get_user_by_telegram_id(telegram_id, service_name)
    if user:
        # 调用服务层的删除用户方法
        success = UserService.delete_user(user)
        if success:
            logger.info(f"用户删除成功: telegram_id={telegram_id}, service_name={service_name}, username={user.username}")
            bot.reply_to(message, "您的账户已成功删除!")
        else:
            logger.error(f"用户删除失败: telegram_id={telegram_id}, service_name={service_name}, username={user.username}")
            bot.reply_to(message, "删除服务器账户失败，本地账户已删除!")
    else:
        logger.warning(f"用户不存在: telegram_id={telegram_id}, service_name={service_name}")
        bot.reply_to(message, "未找到您的账户信息，如已在服务器注册，请使用/bind命令绑定!")

@bot.message_handler(commands=['use_code'])
@user_exists(service_name="navidrome")
def use_invite_code_command(message):
    """
    处理 /use_code 命令，用户使用邀请码注册
    """
    telegram_id = message.from_user.id
    user = UserService.get_user_by_telegram_id(telegram_id, "navidrome")
    if user and user.navidrome_user_id:
        bot.reply_to(message, "您已经注册过了!")
        return

    # 从消息中提取参数
    args = message.text.split()[1:]
    
    if len(args) < 1:
        bot.reply_to(message, "请提供邀请码，格式为：/use_code <[用户名] 邀请码>")
        return
    
    code = args[-1]
    
    # 验证邀请码的有效性
    invite_code = InviteCodeService.get_invite_code(code)
    if not invite_code:
        bot.reply_to(message, "邀请码无效或已过期！")
        return
      
    if invite_code.is_used:
      bot.reply_to(message, "邀请码已被使用")
      return
    
    if invite_code.expire_time < datetime.now():
       bot.reply_to(message, "邀请码已过期")
       return
   
    username = None
    if len(args) == 2:
        username = args[0]
    
    if user.username and user:
        username = user.username
    elif not username:
        bot.reply_to(message, "请提供用户名，格式为：/use_code <用户名> <邀请码>")
        return
    
    password = username # 密码和用户名相同
    # 注册用户
    user = UserService.register_user(telegram_id, "navidrome", username, password)
    if user:
        logger.info(f"用户使用邀请码注册成功: telegram_id={telegram_id}, user_name={user.username}, code={code}")
        bot.reply_to(message, "注册成功!")
        # 使用邀请码
        success = InviteCodeService.use_invite_code(code, telegram_id)
        if not success:
            logger.warning(f"邀请码使用失败：{code}")
        else:
            logger.info(f"邀请码成功使用！")
    else:
        logger.error(f"用户使用邀请码注册失败: telegram_id={telegram_id}, code={code}")
        if len(args) == 2:
           new_username = args[0]
           user = UserService.get_user_by_telegram_id(telegram_id, "navidrome")
           if user:
                user.username = new_username
                user.save()
                logger.info(f"用户名更新成功, new_username={new_username}")
           bot.reply_to(message, f"服务器重名，注册失败，请使用新的用户名，格式为：/use_code <用户名> {code}")
        else:
           bot.reply_to(message, "注册失败，请重试！")
    
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
            logger.info(f"用户积分查询成功: telegram_id={telegram_id}, username={user.username}, score={score}")
            bot.reply_to(message, f"您的积分: {score}")
        else:
            logger.error(f"用户积分查询失败: telegram_id={telegram_id}, username={user.username}")
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
        score = ScoreService.sign_in(user.id)
        if score:
            logger.info(f"用户签到成功: telegram_id={telegram_id}, service_name={service_name}, username={user.username}")
            bot.reply_to(message, f"签到成功! 获得了{score}积分!")
        else:
            logger.warning(f"用户签到失败: telegram_id={telegram_id}, service_name={service_name}")
            bot.reply_to(message, "签到失败，您今天已签到!")
    else:
        logger.warning(f"用户不存在: telegram_id={telegram_id}, service_name={service_name}")
        bot.reply_to(message, "未找到您的账户信息!")

@bot.message_handler(commands=['buyinvite'])
@user_exists("navidrome")
@confirmation_required(f"你确定要购买邀请码嘛？")
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
                    logger.info(f"用户购买邀请码成功: telegram_id={telegram_id}, service_name={service_name}, code={invite_code.code}, username={user.username}")
                    bot.reply_to(message, f"购买邀请码成功，您的邀请码是：<code>{invite_code.code}</code>，请妥善保管！", parse_mode='HTML')
                else:
                    logger.error(f"用户购买邀请码失败，生成邀请码失败: telegram_id={telegram_id}, service_name={service_name}, username={user.username}")
                    bot.reply_to(message, "购买邀请码失败，生成邀请码失败，请重试！")
            else:
                logger.error(f"用户购买邀请码失败，扣除积分失败: telegram_id={telegram_id}, service_name={service_name}, username={user.username}")
                bot.reply_to(message, "购买邀请码失败，扣除积分失败，请重试！")
        else:
            logger.warning(f"用户购买邀请码失败，积分不足: telegram_id={telegram_id}, service_name={service_name}, username={user.username}")
            bot.reply_to(message, f"购买邀请码失败，您的积分不足，邀请码需要 {required_score} 积分！")
    else:
        logger.warning(f"用户不存在: telegram_id={telegram_id}, service_name={service_name}")
        bot.reply_to(message, "未找到您的账户信息!")

@bot.message_handler(commands=['info'])
def info_command(message):
    """
    处理 /info 命令，用户信息查询
    """
    telegram_id = message.from_user.id
    user = UserService.get_user_by_telegram_id(telegram_id, "navidrome")
    if user:
        logger.info(f"user: {user}")
        logger.info(f"用户信息查询成功: telegram_id={telegram_id}, user_id={user.id}")
        response = f"您的信息如下：\n" \
                   f"Telegram ID: {user.telegram_id}\n" \
                   f"用户名: {user.username}\n" \
                   f"积分: {user.score}\n" \
                   f"本地数据库ID: {user.id}\n" \
                   f"Navidrome用户ID: {user.navidrome_user_id}"
        bot.reply_to(message, response)
    else:
        logger.error(f"用户信息查询失败: telegram_id={telegram_id}")
        bot.reply_to(message, "未注册用户，请先注册！")

@bot.message_handler(commands=['give'])
@confirmation_required(f"你确定要赠送积分嘛？")
def give_score_command(message):
    """
    处理 /give 命令，用户赠送积分
     /give <telegram_id> <score>
    """
    telegram_id = message.from_user.id
    service_name = "navidrome"

    logger.info(f"用户请求赠送积分: telegram_id={telegram_id}, service_name={service_name}")

    args = message.text.split()[1:]
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
    sender = UserService.get_user_by_telegram_id(telegram_id, service_name)
    if not sender:
       bot.reply_to(message, "未找到您的账户信息!")
       return
    
    # 检查接收者是否存在
    receiver = UserService.get_user_by_telegram_id(receiver_telegram_id, service_name)
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

@bot.message_handler(commands=['bind'])
def bind_command(message):
    """
    处理 /bind 命令，绑定 Web 服务账户
    /bind <username> <user_id>
    """
    telegram_id = message.from_user.id
    service_name = "navidrome"

    logger.info(f"用户请求绑定账户: telegram_id={telegram_id}, service_name={service_name}")

    args = message.text.split()[1:]
    if len(args) != 2:
        bot.reply_to(message, "参数错误，请提供用户名和用户 ID，格式为：/bind <username> <user_id>")
        return

    username, user_id = args

    # 验证用户
    result = UserService.auth_user_by_id(user_id, username)
    if result:
        logger.info(f"用户绑定账户成功: telegram_id={telegram_id}, service_name={service_name}, username={username}, user_id={user_id}")
        bot.reply_to(message, "账户绑定成功!")
        user = UserService.register_local_user(telegram_id=telegram_id, service_name=service_name, navidrome_user_id=user_id, username=username)
    else:
        logger.error(f"用户绑定账户失败: telegram_id={telegram_id}, service_name={service_name}, username={username}, user_id={user_id}")
        bot.reply_to(message, "账户绑定失败，请重试!")

@bot.message_handler(commands=['unbind'])
def unbind_command(message):
    """
    处理 /unbind 命令，解绑 Web 服务账户并删除本地用户
    """
    telegram_id = message.from_user.id
    service_name = "navidrome"

    logger.info(f"用户请求解绑账户: telegram_id={telegram_id}, service_name={service_name}")

    # 查找本地数据库中的用户
    user = UserService.get_user_by_telegram_id(telegram_id, service_name)
    if user:
        # 删除本地用户
        UserService.delete_local_user(user)
        logger.info(f"用户解绑成功: telegram_id={telegram_id}, service_name={service_name}")
        bot.reply_to(message, "解绑成功！已删除您的本地账户信息。")
    else:
        logger.warning(f"用户不存在: telegram_id={telegram_id}, service_name={service_name}")
        bot.reply_to(message, "未找到您的账户信息！")

@bot.message_handler(commands=['reset_password'])
@user_exists("navidrome")
@confirmation_required(f"你确定要重置密码嘛？")
def reset_password_command(message):
    """
    处理 /reset_password 命令，重置密码
    """
    telegram_id = message.from_user.id
    service_name = "navidrome"

    logger.info(f"用户请求重置密码: telegram_id={telegram_id}, service_name={service_name}")

    args = message.text.split()[1:]
    if len(args) != 1:
        bot.reply_to(message, "参数错误，请提供新密码，格式为：/reset_password <new_password>")
        return

    new_password = args[0]
    user = UserService.get_user_by_telegram_id(telegram_id, service_name)
    if user and UserService.auth_user_by_id(user.navidrome_user_id, user.username):
        # 重置密码
        result = UserService.reset_password(user, new_password=new_password)
        if result:
            logger.info(f"用户重置密码成功: telegram_id={telegram_id}, service_name={service_name}")
            bot.reply_to(message, "密码重置成功！")
        else:
            logger.warning(f"用户不存在: telegram_id={telegram_id}, service_name={service_name}")
            bot.reply_to(message, "密码重置失败，请联系管理员！")
    else:
        logger.warning(f"用户不存在: telegram_id={telegram_id}, service_name={service_name}")
        bot.reply_to(message, "该用户未注册！")
        

@bot.message_handler(commands=['reset_username'])
@user_exists("navidrome")
def reset_username_command(message):
    """
    处理 /reset_username 命令，重置用户名
    """
    telegram_id = message.from_user.id
    service_name = "navidrome"

    logger.info(f"用户请求重置用户名: telegram_id={telegram_id}, service_name={service_name}")

    args = message.text.split()[1:]
    if len(args) != 1:
        bot.reply_to(message, "参数错误，请提供新用户名，格式为：/reset_username <new_username>")
        return

    new_username = args[0]
    user = UserService.get_user_by_telegram_id(telegram_id, service_name)
    if user and user.username != new_username:
        if UserService.auth_user_by_id(user.navidrome_user_id, user.username):
            # 重置用户名
            result = UserService.reset_username(user, new_username=new_username)
            if result:
                UserService.update_user_name(user, new_username)
                logger.info(f"用户重置用户名成功: telegram_id={telegram_id}, service_name={service_name}")
                bot.reply_to(message, f"用户名重置成功，请使用{new_username}登录！")
            else:
                logger.warning(f"服务器出错: telegram_id={telegram_id}, service_name={service_name}")
                bot.reply_to(message, "服务器出错，请联系管理员！")
        else:
            logger.warning(f"服务器无该用户: telegram_id={telegram_id}, service_name={service_name}")
            bot.reply_to(message, "服务器找不到该用户！")
    else:
        logger.warning(f"用户重名: telegram_id={telegram_id}, service_name={service_name}")
        bot.reply_to(message, "用户重名，请重新选择用户名！")
        
            
@bot.message_handler(commands=['random_score'])
@user_exists(service_name='navidrome')
@confirmation_required(f"你确定要发随机红包嘛？")
def random_score_command(message):
    """发送带有按钮的菜单"""
    args = message.text.split()[1:]
    if len(args) != 2:
        bot.reply_to(message, "参数错误，请提供参数，格式为：/random_score <participants_count> <total_score>")
        return
    try:
        participants_count = int(args[0])
        total_score = int(args[1])
    except ValueError:
        bot.reply_to(message, "参数错误，参与人数和总积分数必须是整数！")
        return
    event_id = ScoreService.create_random_score_event(create_user_id=message.from_user.id, telegram_chat_id=message.chat.id, total_score=total_score, participants_count=participants_count)
    if not event_id:
      bot.reply_to(message, "创建积分活动失败")
      return

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("点击抽积分", callback_data=f"random_score_{event_id}")]
        ]
    )
    bot.reply_to(message, "点击按钮参与抽奖！", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith("random_score_"))
def handle_random_score_callback(call):
    """处理随机积分的按钮点击事件"""
    
   
    event_id = int(call.data.split("_")[2])
    user_id = call.from_user.id
    user_name = call.from_user.username if call.from_user.username else call.from_user.first_name #优先获取用户名，如果没有就获取first_name
    user = UserService.get_user_by_telegram_id(user_id, 'navidrome')
    if not user:
        bot.send_message(call.message.chat.id, f"未注册用户[{user_name}](https://t.me/{user_name})，请先注册积分账号。", parse_mode="Markdown", disable_web_page_preview=True)
        logger.info(f"未注册用户{user_name}")
        return
    
    score = ScoreService.use_random_score(event_id=event_id, user_id=user_id, user_name = user_name)
    if score:
        bot.send_message(call.message.chat.id, f"恭喜您[{user_name}](https://t.me/{user_name})，获得{score}积分！", parse_mode="Markdown", disable_web_page_preview=True)
        event_data = ScoreService.get_random_score_event(event_id)
        if event_data and event_data['is_finished']:
           score_result = json.loads(event_data['score_result'])
           response = f"积分已经分发完毕, 中奖信息如下：\n"
           response += f"---------------------------\n"
           for item in score_result:
             response += f"用户: [{item['user_name']}](https://t.me/{item['user_name']}), 获取积分： {item['score']}\n"
           bot.send_message(call.message.chat.id, response, parse_mode="Markdown", disable_web_page_preview=True)
    elif score == 0:
       bot.send_message(call.message.chat.id, f"积分已经分发完毕")
    else:
        bot.send_message(call.message.chat.id, f"[{user_name}](https://t.me/{user_name})您已经获取过奖励/未注册！", parse_mode="Markdown", disable_web_page_preview=True)
        