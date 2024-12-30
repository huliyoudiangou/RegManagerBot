# 管理员命令处理器
import telebot
from app.bot.validators import admin_required
from app.services.user_service import UserService
from app.services.score_service import ScoreService
from app.services.invite_code_service import InviteCodeService
from app.utils.logger import logger
from config import settings
from app.bot.core.bot_instance import bot
from app.utils.api_clients import navidrome_api_client

# 需要安装的模块：无


@bot.message_handler(commands=['generate_code'])
@admin_required
def generate_invite_code_command(message):
    """生成邀请码 (管理员命令)"""
    telegram_id = message.from_user.id
    
    args = message.text.split()[1:]
    if len(args) == 0:
        count = 1 # 默认生成 1 个
    else:
      try:
          count = int(args[0])
      except ValueError:
        bot.reply_to(message, "参数错误，邀请码数量必须是整数！")
        return

    if count <= 0:
        bot.reply_to(message, "邀请码数量必须大于 0！")
        return

    invite_codes = []
    for _ in range(count):
      invite_code = InviteCodeService.generate_invite_code(telegram_id)
      if invite_code:
        invite_codes.append(invite_code.code)
      else:
        bot.reply_to(message, "邀请码生成失败，请重试！")
        return
    
    if invite_codes:
      response = f"成功生成{count}个邀请码:\n" + "\n".join(invite_codes)
      bot.reply_to(message, response)
      
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

@bot.message_handler(commands=['set_price'])
@admin_required
def set_price_command(message):
    """
    设置邀请码价格 (管理员命令)
    /set_price <price>
    """
    telegram_id = message.from_user.id
    logger.info(f"管理员设置邀请码价格: telegram_id={telegram_id}")

    args = message.text.split()[1:]
    if len(args) != 1:
        bot.reply_to(message, "参数错误，请提供价格，格式为：/set_price <price>")
        return

    try:
        price = int(args[0])
    except ValueError:
        bot.reply_to(message, "价格必须是整数！")
        return

    config_name = "INVITE_CODE_PRICE" # 直接指定配置项
    # 更新配置
    setattr(settings, config_name, price) # 只更新 config 对象中的值
    logger.info(f"配置项 {config_name} 已更新为 {price}")
    bot.reply_to(message, f"邀请码积分价格已更新为 {price}")

@bot.message_handler(commands=['userinfo'])
@admin_required
def get_user_info_by_telegram_id_command(message):
    """
    根据 Telegram ID 查询用户信息 (管理员命令)
    /userinfo <telegram_id>
    """
    telegram_id = message.from_user.id
    service_name = "navidrome"
    logger.info(f"管理员根据 Telegram ID 查询用户信息: telegram_id={telegram_id}, service_name={service_name}")

    args = message.text.split()[1:]
    if len(args) != 1:
        bot.reply_to(message, "参数错误，请提供用户 Telegram ID，格式为：/userinfo <telegram_id>")
        return

    try:
        target_telegram_id = int(args[0])
    except ValueError:
        bot.reply_to(message, "参数错误，用户 Telegram ID 必须是整数！")
        return

    # 查找本地数据库中的用户
    user = UserService.get_user_by_telegram_id(target_telegram_id, service_name)
    if user:
       logger.info(f"用户查询成功: telegram_id={target_telegram_id}, user_id={user.id}")
       response = f"用户信息如下：\n" \
                 f"Telegram ID: {user.telegram_id}\n" \
                 f"用户名: {user.username}\n" \
                 f"积分: {user.score}\n" \
                 f"本地数据库ID: {user.id}\n" \
                 f"Navidrome用户ID: {user.navidrome_user_id}"
       bot.reply_to(message, response)
    else:
        logger.warning(f"用户不存在: telegram_id={target_telegram_id}, service_name={service_name}")
        bot.reply_to(message, f"未找到用户: {target_telegram_id}")

@bot.message_handler(commands=['userinfo_by_username'])
@admin_required
def get_user_info_by_username_command(message):
    """
    根据用户名查询用户信息 (管理员命令)
    /userinfo_by_username <username>
    """
    telegram_id = message.from_user.id
    service_name = "navidrome"
    logger.info(f"管理员根据用户名查询用户信息: telegram_id={telegram_id}, service_name={service_name}")

    args = message.text.split()[1:]
    if len(args) != 1:
        bot.reply_to(message, "参数错误，请提供用户名，格式为：/userinfo_by_username <username>")
        return

    username = args[0]
    
    # 在本地数据库中查找用户
    user = UserService.get_user_by_username(username)
    if user:
        logger.info(f"用户查询成功: username={username}, user_id={user.id}")
        response = f"用户信息如下：\n" \
                f"Telegram ID: {user.telegram_id}\n" \
                f"用户名: {user.username}\n" \
                f"积分: {user.score}\n" \
                f"本地数据库ID: {user.id}\n" \
                f"Navidrome用户ID: {user.navidrome_user_id}"
        bot.reply_to(message, response)
        return

    # 如果没有找到用户，返回错误信息
    else:
        bot.reply_to(message, f"未找到用户: {username}")
        logger.warning(f"未找到用户: username={username}")
    
@bot.message_handler(commands=['stats'])
@admin_required
def get_stats_command(message):
    """
    获取统计信息 (管理员命令)
    /stats
    """
    telegram_id = message.from_user.id
    service_name = "navidrome"
    logger.info(f"管理员查询统计信息: telegram_id={telegram_id}, service_name={service_name}")
    
    try:
      # 获取本地数据库用户数量
      users = UserService.get_all_users()
      local_user_count = len(users) if users else 0
      
      # 获取 Navidrome 用户数量
      navidrome_users = navidrome_api_client.get_users()
    #   web_user_count = len(navidrome_users['data']) if navidrome_users and navidrome_users['status'] == 'success' else 0
      web_user_count = navidrome_users['headers']['x-total-count']
      # 获取 Navidrome 歌曲总数
      songs = navidrome_api_client.get_songs()
      song_count = int(songs['x-total-count']) if songs and 'x-total-count' in songs else 0

      # 获取 Navidrome 专辑总数
      albums = navidrome_api_client.get_albums()
      album_count = int(albums['x-total-count']) if albums and 'x-total-count' in albums else 0
      
      # 获取 Navidrome 艺术家总数
      artists = navidrome_api_client.get_artists()
      artist_count = int(artists['x-total-count']) if artists and 'x-total-count' in artists else 0

      # 获取 Navidrome 电台总数
      radios = navidrome_api_client.get_radios()
      radio_count = int(radios['x-total-count']) if radios and 'x-total-count' in radios else 0

      response = f"统计信息:\n" \
                f"本地数据库注册用户数量: {local_user_count}\n" \
               f"Navidrome Web 应用用户数量: {web_user_count}\n"
      response += f"-------\n"
      response += f"Navidrome 歌曲总数: {song_count}\n"
      response += f"Navidrome 专辑总数: {album_count}\n"
      response += f"Navidrome 艺术家总数: {artist_count}\n"
      response += f"Navidrome 电台总数: {radio_count}\n"
      response += f"-------\n"
      response += f"清理系统的状态为：{settings.ENABLE_EXPIRED_USER_CLEAN}\n"
      response += f"邀请码系统的状态为：{settings.INVITE_CODE_SYSTEM_ENABLED}\n"
      bot.reply_to(message, response)
      logger.info(f"管理员获取注册状态成功: telegram_id={telegram_id}, 本地注册用户数量={local_user_count},  Navidrome Web 应用用户数量={web_user_count}, 歌曲总数={song_count}, 专辑总数={album_count}, 艺术家总数={artist_count}, 电台总数={radio_count}")
    except Exception as e:
      logger.error(f"获取注册状态失败: telegram_id={telegram_id}, error={e}")
      bot.reply_to(message, "获取注册状态失败，请重试！")


@bot.message_handler(commands=['toggle_expired_user_clean'])
@admin_required
def toggle_expired_user_clean_command(message):
    """开启/关闭过期用户清理定时任务 (管理员命令)"""
    settings.ENABLE_EXPIRED_USER_CLEAN = not settings.ENABLE_EXPIRED_USER_CLEAN
    logger.debug(f'清理系统的状态为：{settings.ENABLE_EXPIRED_USER_CLEAN}')

    UserService.start_clean_expired_users()

    logger.info(f"过期用户清理定时任务已更改: {settings.ENABLE_EXPIRED_USER_CLEAN}")
    bot.reply_to(message, f"过期用户清理定时任务已{'开启' if settings.ENABLE_EXPIRED_USER_CLEAN else '关闭'}")

@bot.message_handler(commands=['get_expired_users'])
@admin_required
def get_expired_users_command(message):
    """获取已过期的用户 (管理员命令)"""
    telegram_id = message.from_user.id
    logger.info(f"管理员请求获取已过期的用户列表: telegram_id={telegram_id}")

    expired_users = UserService.get_expired_users()
    
    if expired_users and 'expired' in expired_users and expired_users['expired']:
        count = 0
        response = "已过期的用户列表：\n"
        response += f"序号: 用户名\n"
        response += f"-----------\n"
        for user in expired_users['expired']:
            response += f"{count+1}: {user['username']}\n"
            count = count + 1
        response += f"-----------\n"
        response += f"已过期的用户一共有：{count}位！\n"
        # bot.reply_to(message, response)
        bot.reply_to(message, f"已过期的用户列表成功，共有{count}位！")
        logger.info(f"管理员获取已过期的用户列表成功，共有{count}位！")
    else:
        bot.reply_to(message, "没有已过期的用户!")
        logger.warning(f"没有已过期的用户: telegram_id={telegram_id}")
        
@bot.message_handler(commands=['get_expiring_users'])
@admin_required
def get_expiring_users_command(message):
    """获取即将过期的用户 (管理员命令)"""
    telegram_id = message.from_user.id
    logger.info(f"管理员请求获取即将过期的用户列表: telegram_id={telegram_id}")

    expiring_users = UserService.get_expired_users()
    
    if expiring_users and 'warning' in expiring_users and expiring_users['warning']:
        count = 0
        response = "即将过期的用户列表：\n"
        response += f"序号: 用户名\n"
        response += f"-----------\n"
        for user in expiring_users['warning']:
            response += f"{count+1}: {user['username']}\n"
        response += f"-----------\n"
        response += f"即将过期的用户一共有：{count}位！\n"
        # bot.reply_to(message, response)
        bot.reply_to(message, f"即将过期的用户列表成功，共有{count}位！")
        logger.info(f"管理员获取即将过期的用户列表成功: 共有{count}位！")
    else:
        bot.reply_to(message, "没有即将过期的用户!")
        logger.warning(f"没有即将过期的用户: telegram_id={telegram_id}")

@bot.message_handler(commands=['clean_expired_users'])
@admin_required
def clean_expired_users_command(message):
    """立即清理过期用户 (管理员命令)"""
    telegram_id = message.from_user.id
    logger.info(f"管理员请求清理过期用户: telegram_id={telegram_id}")

    user_list = UserService.clean_expired_users()
    if user_list:
        bot.reply_to(message, f"已执行过期用户清理,一共清理用户{len(user_list)}位！")
        logger.info(f"管理员清理过期用户成功: telegram_id={telegram_id}")
    else:
        bot.reply_to(message, "未发现过期用户！")
        logger.info(f"没有用户过期！")