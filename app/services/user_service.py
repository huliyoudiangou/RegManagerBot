from app.models import User, ServiceUser
from app.utils.api_clients import service_api_client
from app.utils.logger import logger
from config import settings
from datetime import datetime, timedelta
import pytz
import operator


# 需要安装的模块：无

class UserService:
    """
    用户服务
    """

    @staticmethod
    def register_local_user(telegram_id, service_user_id=None, service_type=settings.SERVICE_TYPE, username=None,
                            invite_code=None, expired_days=settings.CREATE_USER_EXPIRED_DAYS):
        # 在本地数据库中创建用户
        user = ServiceUser.get_by_telegram_id_and_service_type(telegram_id=telegram_id)
        expiration_date = datetime.now() + timedelta(days=expired_days)
        if not user:
            user = ServiceUser(telegram_id=telegram_id, service_type=service_type, service_user_id=service_user_id,
                               username=username, invite_code=invite_code, expiration_date=expiration_date)
            user.save()
            logger.debug(f"本地用户创建成功: username={username}")
            return user
        else:
            user = ServiceUser(id=user.id, telegram_id=telegram_id, score=user.score, service_type=service_type,
                               service_user_id=service_user_id, username=username, invite_code=invite_code,
                               expiration_date=expiration_date)
            user.save()
            logger.debug(f"本地用户更新成功: username={username}")
            return user

    @staticmethod
    def register_user(telegram_id, service_type, username, password, email=None, code=None,
                      expired_days=settings.CREATE_USER_EXPIRED_DAYS):
        """
        注册用户

        Args:
            telegram_id: Telegram ID
            service_type: 服务名称，例如 "navidrome"
            username: 用户名 (在对应web应用中的用户名)
            password: 密码 (在对应web应用中的密码)

        Returns:
            注册成功的用户对象，如果注册失败则返回 None
        """
        # service_type = settings.SERVICE_TYPE
        logger.debug(
            f"开始注册用户: telegram_id={telegram_id}, service_type={service_type}， username={username}, password={password}")

        result = service_api_client.create_user(username, password)
        if result and result['status'] == 'success':
            match settings.SERVICE_TYPE:
                case "navidrome":
                    service_user_id = result['data']['id']
                case "emby":
                    service_user_id = result['data']['Id']
                case "audiobookshelf":
                    service_user_id = result['data']['user']['id']
                case _:
                    service_user_id = None
                    logger.warning(f"不支持的服务类型：{service_type}")
            logger.debug(f"{service_type} 用户创建成功: service_user_id={service_user_id}")
        else:
            logger.error(f"{service_type} 用户创建失败: {result}")
            return None

        user = ServiceUser.get_by_telegram_id_and_service_type(telegram_id, service_type)
        expiration_date = datetime.now() + timedelta(days=expired_days)
        if not user:
            # 在本地数据库中创建用户
            user = ServiceUser(telegram_id=telegram_id, service_type=service_type, service_user_id=service_user_id,
                               username=username, invite_code=code, expiration_date=expiration_date)
            user.save()
            logger.debug(f"本地用户创建成功: user_id={user.id}")
            return user
        else:
            user = ServiceUser(id=user.id, score=user.score, telegram_id=user.telegram_id, service_type=user.service_type,
                               service_user_id=service_user_id, username=username, invite_code=user.invite_code,
                               expiration_date=expiration_date)
            user.save()
            logger.debug(f"本地用户更新成功: user_id={user.id}")
            return user

    @staticmethod
    def delete_local_user(user):
        """删除用户"""
        if user.service_type:
            # 删除本地用户
            user.delete()
            logger.warning(f"本地用户删除成功: user_name={user.username}")
            return True
        else:
            logger.error(f"{user.service_type} 用户删除失败")
            return False

    @staticmethod
    def delete_user(user):
        """删除用户"""
        result = service_api_client.delete_user(user.service_user_id)
        if result and result['status'] == 'success':
            logger.warning(f"{user.service_type} 用户删除成功: user_id={user.service_user_id}")
            # 删除本地用户
            user.delete()
            logger.warning(f"本地用户删除成功: user_id={user.id}")
            return True
        else:
            user.delete()
            logger.error(f"{user.service_type} 用户删除失败: {result}")
            return False

    @staticmethod
    def get_user_by_telegram_id(telegram_id, service_type=None):
        """
        根据 Telegram ID 和服务名称查询用户

        Args:
            telegram_id: Telegram ID
            service_type: 服务名称

        Returns:
            User 对象，如果用户不存在则返回 None
        """
        logger.debug(f"查询用户: telegram_id={telegram_id}")
        user = ServiceUser.get_by_telegram_id_and_service_type(telegram_id, service_type)
        logger.debug(f"{user}")
        if user and user.service_type:
            if user.service_type:
                logger.debug(f"获取用户信息成功: {user.username}, 服务：{user.service_type}")
                return user

            else:
                logger.error(f"不支持的服务名称: {user.service_type}")
                return None
        else:
            logger.warning(f"用户不存在: telegram_id={telegram_id}")
            return None

    @staticmethod
    def get_user_by_id(user_id):
        """
        根据用户 ID 查询用户

        Args:
            user_id: 用户 ID

        Returns:
            User 对象，如果用户不存在则返回 None
        """
        logger.debug(f"查询用户: user_id={user_id}")
        user = ServiceUser.get_by_id(user_id)
        if user:
            logger.debug(f"用户查询成功: user={user}")
            return user
        else:
            logger.warning(f"用户不存在: user_id={user_id}")
            return None

    @staticmethod
    def get_user_by_service_user_id(user_id):
        """
        根据用户 service_user_id 查询用户

        Args:
            user_id: service_user_id

        Returns:
            ServiceUser 对象，如果用户不存在则返回 None
        """
        logger.debug(f"查询用户: user_id={user_id}")
        user = ServiceUser.get_by_service_id(user_id)
        if user:
            logger.debug(f"用户查询成功: user={user}")
            return user
        else:
            logger.warning(f"用户不存在: user_id={user_id}")
            return None

    @staticmethod
    def get_user_by_username(username):
        """
        根据用户 username 查询用户

        Args:
            username: 用户 username

        Returns:
            ServiceUser 对象，如果用户不存在则返回 None
        """
        logger.debug(f"查询用户: username={username}")
        user = ServiceUser.get_by_username(username)
        if user:
            logger.debug(f"用户查询成功: user={user}")
            return user
        else:
            logger.warning(f"用户不存在: username={username}")
            return None

    @staticmethod
    def get_all_users(service_type=None):
        """获取所有用户"""
        logger.debug("获取所有用户")
        users = ServiceUser.get_all(service_type)
        if users:
            logger.debug(f"获取所有用户成功: users={users}")
            return users
        else:
            logger.warning("获取所有用户失败")
            return None

    @staticmethod
    def is_admin(telegram_id):
        """
        检查用户是否是管理员

        Args:
            telegram_id: Telegram ID

        Returns:
            True 如果是管理员，否则返回 False
        """
        logger.debug(f"检查用户是否是管理员: telegram_id={telegram_id}")
        is_admin = telegram_id in settings.ADMIN_TELEGRAM_IDS
        logger.debug(f"检查结果: {is_admin}")
        return is_admin

    @staticmethod
    def update_user_score(user, score):
        """更新用户积分"""
        user.score = score
        user.save()
        logger.debug(f"用户积分更新成功: user_id={user.id}, score={user.score}")
        return user

    @staticmethod
    def auth_user_by_username_and_password(username, password):
        """认证用户绑定"""
        user_id = service_api_client.auth_user(username, password)
        if user_id:
            logger.info(f"用户认证成功: service_user_id={user_id['id']}")
            return user_id['id']
        else:
            logger.error(f"服务器未找到该用户！: {username}")
            return False

    @staticmethod
    def reset_password(user, new_password):
        """重置密码"""
        result = service_api_client.update_username_or_password(user.service_user_id, username=user.username,
                                                                password=new_password)

        if result and result['status'] == 'success':
            logger.debug("密码重置成功")
            return True
        else:
            logger.error(f"密码重置失败: {result}")
            return False

    @staticmethod
    def update_user_telegram_id(user, telegram_id):
        """更新本地数据库中的用户telegram_id"""
        logger.debug(f"更新用户Telegram ID")
        user.telegram_id = telegram_id
        user.save()
        logger.debug(f"用户Telegram ID更新成功！")
        return user
    
    @staticmethod
    def update_user_name(user, username):
        """更新本地数据库中的用户名"""
        logger.debug(f"用户重置为：{username}")
        return ServiceUser.update_username(user.telegram_id, username)

    @staticmethod
    def reset_username(user, new_username):
        """重置用户名"""
        result = service_api_client.update_username_or_password(user.service_user_id, username=new_username)

        if result and result['status'] == 'success':
            logger.debug(f"用户重置为：{new_username}")
            return True
        else:
            logger.error(f"用户重置用户名失败: {result}")
            return False

    @staticmethod
    def clean_expired_users():
        """清理过期用户"""
        logger.warning("开始清理过期用户")
        expired_users = service_api_client._get_expired_users()
        if 'warning' in expired_users and expired_users['warning']:
            for user in expired_users['warning']:
                logger.warning(f"用户将在3天后过期，请注意: service_user_id={user['service_user_id']}")
        if 'expired' in expired_users and expired_users['expired']:
            user_list = []
            for user in expired_users['expired']:
                u = ServiceUser.get_by_service_id(user['service_user_id'])
                if u.status == 'whitelist':
                    logger.info(f"发现白名单用户{user['username']}, 不处理！")
                    pass
                else:
                    logger.warning(f"删除过期用户: service_user_id={user['service_user_id']}")
                    service_api_client.delete_user(user['service_user_id'])
                    user_list.append(user['username'])
                    navi = ServiceUser.get_by_service_id(user['service_user_id'])
                    if navi:
                        logger.warning(f"删除本地过期用户: telegram_id={navi.telegram_id}")
                        navi.delete()
                    else:
                        logger.warning("本地无用户信息，无需删除！")
                        pass
            return user_list

    @staticmethod
    def get_expired_users():
        """获取过期用户和即将过期的用户"""
        logger.debug("获取过期用户和即将过期的用户")
        expired_users = service_api_client._get_expired_users()
        return expired_users

    @staticmethod
    def start_clean_expired_users():
        """启动和关闭清理系统"""
        logger.debug("准备关闭/开启清理系统")
        service_api_client.start_clean_expired_users()

    @staticmethod
    def get_users_by_register_time(start_time=None, end_time=None):
        """
      获取指定注册时间范围内注册的用户
      Args:
        start_time:  开始时间，日期字符串，例如 '2024-12-25'
        end_time: 结束时间，日期字符串，例如 '2024-12-30'
      Returns:
        符合条件的用户列表
      """
        logger.debug(f"获取指定注册时间范围内注册的用户, start_time={start_time}, end_time={end_time}")
        if start_time is None and end_time is None:
            logger.debug(f"未指定时间区间，获取所有用户的列表")
            return UserService.get_all_users()

        try:
            start_date = datetime.strptime(start_time, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_time, "%Y-%m-%d").date()
        except ValueError:
            logger.warning(f"时间格式错误, 请使用 'YYYY-MM-DD'格式, start_time={start_time}, end_time={end_time}")
            return []
        users = UserService.get_all_users()
        if not users:
            logger.warning("没有用户，无法获取签到用户列表！")
            return []

        user_list = [user for user in users if hasattr(user, 'id') and user.id and User.get_by_id(
            user.id).create_time and start_date <= User.get_by_id(user.id).create_time.date() <= end_date]
        logger.debug(
            f"获取指定注册时间范围内注册的用户成功, start_time={start_time}, end_time={end_time}, count={len(user_list)}")
        return user_list

    @staticmethod
    def get_sign_in_users(time_range="today"):
        """
        获取指定时间范围内签到的用户
    
        Args:
            time_range: 时间范围，例如 "today", "yesterday", "2024-12-25"
    
        Returns:
            符合条件的用户列表
        """
        logger.debug(f"获取签到用户列表，时间范围: {time_range}")
        shanghai_tz = pytz.timezone('Asia/Shanghai')
        now_shanghai = datetime.now(shanghai_tz)
        users = UserService.get_all_users()
        if not users:
            logger.warning("没有用户，无法获取签到用户列表！")
            return []

        user_list = []
        if time_range == "today":
            user_list = [user for user in users if hasattr(user,
                                                           'last_sign_in_date') and user.last_sign_in_date and user.last_sign_in_date.astimezone(
                shanghai_tz).date() == now_shanghai.date()]
        elif time_range == "yesterday":
            yesterday_shanghai = now_shanghai - timedelta(days=1)
            user_list = [user for user in users if hasattr(user,
                                                           'last_sign_in_date') and user.last_sign_in_date and user.last_sign_in_date.astimezone(
                shanghai_tz).date() == yesterday_shanghai.date()]
        elif isinstance(time_range, str) and len(time_range) == 10 and time_range[4] == "-" and time_range[7] == "-":
            try:
                target_date = datetime.strptime(time_range, "%Y-%m-%d").date()
                user_list = [user for user in users if hasattr(user,
                                                               'last_sign_in_date') and user.last_sign_in_date and user.last_sign_in_date.astimezone(
                    shanghai_tz).date() == target_date]
            except ValueError:
                logger.warning(f"时间格式错误，请使用YYYY-MM-DD格式，使用today查询，time_range={time_range}")
                user_list = [user for user in users if hasattr(user,
                                                               'last_sign_in_date') and user.last_sign_in_date and user.last_sign_in_date.astimezone(
                    shanghai_tz).date() == now_shanghai.date()]
        else:
            logger.warning(f"不支持的时间范围: {time_range}, 使用today查询")
            user_list = [user for user in users if hasattr(user,
                                                           'last_sign_in_date') and user.last_sign_in_date and user.last_sign_in_date.astimezone(
                shanghai_tz).date() == now_shanghai.date()]

        logger.debug(f"成功获取签到用户列表: {time_range}, count={len(user_list)}")
        return user_list

    @staticmethod
    def get_info_in_service_by_user_id(user_id):
        """通id获取服务器中注册信息

        Args:
            user_id (str): 服务器中的用户名id
        """
        user = service_api_client.get_user(user_id)
        if user:
            logger.debug(f"获取用户信息成功: {user}")
            return user
        else:
            logger.error(f"获取用户信息失败: {user}")
            return None

    @staticmethod
    def get_info_in_server(user_name):
        """通过用户名获取服务器中注册信息

        Args:
            user_name (str): 服务器中的用户名
        """
        user = service_api_client.get_user_by_username(user_name)
        if user:
            logger.debug(f"获取用户信息成功: {user}")
            return user
        else:
            logger.error(f"获取用户信息失败: {user}")
            return None

    @staticmethod
    def get_score_chart(limit=10):
        """获取积分排行榜"""
        logger.debug(f"获取积分排行榜，limit={limit}")
        users = UserService.get_all_users()
        if not users:
            logger.warning("没有用户，无法获取排行榜")
            return []

        # 按积分降序排序
        sorted_users = sorted(users, key=operator.attrgetter('score'), reverse=True)

        # 获取指定数量的用户
        top_users = sorted_users[:limit]

        # 创建排行榜数据列表
        rank = 1
        chart = []
        for user in top_users:
            chart.append(
                {"rank": rank, "telegram_id": user.telegram_id, "username": user.username, "score": user.score})
            rank += 1
        logger.debug(f"获取积分排行榜成功, limit={limit}")
        return chart

    @staticmethod
    def get_user_status(user_id):
        """获取用户状态"""
        logger.debug(f"获取用户状态: user_id={user_id}")
        user = UserService.get_user_by_id(user_id)
        if user:
            logger.debug(f"获取用户状态成功: user={user.username}")
            return user.status
        else:
            logger.warning(f"获取用户状态失败: user_id={user_id}")
            return None

    @staticmethod
    def set_user_status(user_id, new_status):
        """设置用户状态"""
        logger.debug(f"设置用户状态: user_id={user_id}, new_status={new_status}")
        user = UserService.get_user_by_id(user_id)
        if user:
            user.status = new_status
            user.save()
            logger.debug(f"设置用户状态成功: user={user.username}")
            return user
        else:
            logger.warning(f"设置用户状态失败: user_id={user_id}")
            return None

    @staticmethod
    def clear_user_by_expired(user_id, del_server_user=False):
        """清理过期用户"""
        logger.debug(f"清理过期用户: user_id={user_id}")
        user = UserService.get_user_by_id(user_id)
        if user:
            user.delete()
            logger.debug(f"清理本地过期用户成功: user={user}")
        else:
            logger.warning(f"清理本地过期用户失败: user_id={user_id}")
            return False

        if del_server_user:
            service_api_client.delete_user(user.service_user_id)
            logger.debug(f"清理服务器过期用户成功: user={user.username}")
        else:
            logger.warning(f"清理服务器过期用户失败: user_id={user_id}")
            return False

    @staticmethod
    def block_user(user_id):
        """封禁用户"""
        logger.debug(f"封禁用户: user_id={user_id}")
        user = UserService.get_user_by_id(user_id)
        if user:
            user.status = "blocked"
            user.save()
            logger.debug(f"封禁用户成功: user={user.username}")
            return user
        else:
            logger.warning(f"封禁用户失败: user_id={user_id}")
            return None

    @staticmethod
    def unblock_user(user_id):
        """解封用户"""
        logger.debug(f"解封用户: user_id={user_id}")
        user = UserService.get_user_by_id(user_id)
        if user:
            user.status = "active"
            user.save()
            logger.debug(f"解封用户成功: user={user.username}")
            return user
        else:
            logger.warning(f"解封用户失败: user_id={user_id}")
            return None

    @staticmethod
    def block_server_user(user_id):
        """封禁服务器用户"""
        logger.debug(f"封禁服务器用户: user_id={user_id}")
        user = UserService.get_user_by_id(user_id)
        if user:
            service_api_client.block_user(user.service_user_id)
            logger.debug(f"封禁服务器用户成功: user={user.username}")
            return user
        else:
            logger.warning(f"封禁服务器用户失败: user_id={user_id}")
            return None

    @staticmethod
    def unblock_server_user(user_id):
        """解封服务器用户"""
        logger.debug(f"解封服务器用户: user_id={user_id}")
        user = UserService.get_user_by_id(user_id)
        if user:
            service_api_client.unblock_user(user.service_user_id)
            logger.debug(f"解封服务器用户成功: user={user.username}")
            return user
        else:
            logger.warning(f"解封服务器用户失败: user_id={user_id}")
            return None

    @staticmethod
    def get_block_users():
        """获取封禁用户"""
        logger.debug("获取封禁用户")
        users = UserService.get_all_users()
        block_users = {}
        if users:
            for user in users:
                if user.status == "blocked":
                    logger.debug(f"获取封禁用户成功: user={user.username}")
                    block_users.update({"username": user.username, "telegram_id": user.telegram_id})
            return block_users
        else:
            logger.debug("获取封禁用户失败")
            return

