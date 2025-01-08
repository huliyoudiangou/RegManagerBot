from app.models import User, ServiceUser
from app.utils.api_clients import service_api_client
from app.utils.logger import logger
from config import settings
from datetime import datetime
import pytz
import operator

# 需要安装的模块：无

class UserService:
    """
    用户服务
    """
    @staticmethod
    def register_local_user(telegram_id, service_user_id=None, service_type=settings.SERVICE_TYPE, username=None):
        # 在本地数据库中创建用户
        user = ServiceUser.get_by_telegram_id_and_service_type(telegram_id=telegram_id)
        if not user:
            user = ServiceUser(telegram_id=telegram_id, service_type=service_type, service_user_id=service_user_id, username=username)
            user.save()
            logger.debug(f"本地用户创建成功: username={username}")
            return user
        else:
            user = ServiceUser(id=user.id, telegram_id=telegram_id, service_type=service_type, service_user_id=service_user_id, username=username)
            user.save()
            logger.debug(f"本地用户更新成功: username={username}")
            return user
            
    @staticmethod
    def register_user(telegram_id, service_type, username, password, email=None, code=None):
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
        logger.debug(f"开始注册用户: telegram_id={telegram_id}, service_type={service_type}， username={username}, password={password}")
        
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
                    logger.warning(f"不支持的服务类型：{service_type}")
            logger.debug(f"{service_type} 用户创建成功: service_user_id={service_user_id}")
        else:
            logger.error(f"{service_type} 用户创建失败: {result}")
            return None
        
        user = ServiceUser.get_by_telegram_id_and_service_type(telegram_id, service_type)
        if not user:
            # 在本地数据库中创建用户
            user = ServiceUser(telegram_id=telegram_id, service_type=service_type, service_user_id=service_user_id, username=username, invite_code=code)
            user.save()
            logger.debug(f"本地用户创建成功: user_id={user.id}")
            return user
        else:
            user = ServiceUser(id=user.id, score=user.score, telegram_id=telegram_id, service_type=service_type, service_user_id=service_user_id, username=username, invite_code=code)
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
    def get_user_by_telegram_id(telegram_id):
        """
        根据 Telegram ID 和服务名称查询用户

        Args:
            telegram_id: Telegram ID
            service_type: 服务名称

        Returns:
            User 对象，如果用户不存在则返回 None
        """
        logger.debug(f"查询用户: telegram_id={telegram_id}")
        user = ServiceUser.get_by_telegram_id_and_service_type(telegram_id)
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
        user = ServiceUser.get_by_service_user_id(user_id)
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
    def get_all_users():
      """获取所有用户"""
      logger.debug("获取所有用户")
      users = ServiceUser.get_all()
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
    def auth_user_by_id(user_id, username):
        """认证用户绑定"""
        user = service_api_client.get_user(user_id)
        if user and user['status'] == 'success':
            match settings.SERVICE_TYPE:
                case "navidrome":
                    if user['data']['userName'] == username:
                        logger.debug(f"用户认证成功: user_id={user_id}, name={username}")
                        return user
                    else:
                        logger.warning(f"用户认证失败: user_id={user_id}, name={username}")
                        return False
                case "emby":
                    if user['data']['Name'] == username:
                        logger.debug(f"用户认证成功: user_id={user_id}, name={username}")
                        return user
                    else:
                        logger.warning(f"用户认证失败: user_id={user_id}, name={username}")
                        return False
                case "audiobookshelf":
                    if user['data']['username'] == username:
                        logger.debug(f"用户认证成功: user_id={user_id}, name={username}")
                        return user
                    else:
                        logger.warning(f"用户认证失败: user_id={user_id}, name={username}")
                        return False
                case _:
                    logger.warning("不支持的服务认证")
                    return False
        else:
            logger.error(f"服务器未找到该用户！: {username}")
            return False
            

    @staticmethod
    def reset_password(user, new_password):
        """重置密码"""
        result = service_api_client.update_user(user.service_user_id, username=user.username, password=new_password)
            
        if result and result['status'] == 'success':
            logger.debug("密码重置成功")
            return True
        else:
            logger.error(f"密码重置失败: {result}")
            return False
    
    @staticmethod
    def update_user_name(user, username):
        """更新本地数据库中的用户名"""
        logger.debug(f"用户重置为：{username}")
        return ServiceUser.update_username(user.telegram_id, username)
  
    @staticmethod
    def reset_username(user, new_username):
        """重置用户名"""
        result = service_api_client.update_user(user.service_user_id, username=new_username)
            
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
                logger.warning(f"删除过期用户: service_user_id={user['service_user_id']}")
                service_api_client.delete_user(user['service_user_id'])
                user_list.append(user['username'])
                navi = ServiceUser.get_by_service_user_id(user['service_user_id'])
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

      user_list = [user for user in users if hasattr(user, 'id') and user.id and User.get_by_id(user.id).create_time and start_date <= User.get_by_id(user.id).create_time.date() <= end_date]
      logger.debug(f"获取指定注册时间范围内注册的用户成功, start_time={start_time}, end_time={end_time}, count={len(user_list)}")
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
          user_list = [user for user in users if hasattr(user, 'last_sign_in_date') and user.last_sign_in_date and user.last_sign_in_date.astimezone(shanghai_tz).date() == now_shanghai.date() ]
        elif time_range == "yesterday":
          yesterday_shanghai = now_shanghai - datetime.timedelta(days=1)
          user_list = [user for user in users if hasattr(user, 'last_sign_in_date') and user.last_sign_in_date and user.last_sign_in_date.astimezone(shanghai_tz).date() == yesterday_shanghai.date() ]
        elif isinstance(time_range, str) and len(time_range) == 10 and time_range[4] == "-" and time_range[7] == "-":
            try:
                target_date = datetime.strptime(time_range, "%Y-%m-%d").date()
                user_list = [user for user in users if hasattr(user, 'last_sign_in_date') and user.last_sign_in_date and user.last_sign_in_date.astimezone(shanghai_tz).date() == target_date]
            except ValueError:
               logger.warning(f"时间格式错误，请使用YYYY-MM-DD格式，使用today查询，time_range={time_range}")
               user_list = [user for user in users if hasattr(user, 'last_sign_in_date') and user.last_sign_in_date and user.last_sign_in_date.astimezone(shanghai_tz).date() == now_shanghai.date() ]
        else:
          logger.warning(f"不支持的时间范围: {time_range}, 使用today查询")
          user_list = [user for user in users if hasattr(user, 'last_sign_in_date') and user.last_sign_in_date and user.last_sign_in_date.astimezone(shanghai_tz).date() == now_shanghai.date()]

        logger.debug(f"成功获取签到用户列表: {time_range}, count={len(user_list)}")
        return user_list

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
        chart.append({"rank": rank, "telegram_id": user.telegram_id, "username": user.username, "score": user.score})
        rank += 1
      logger.debug(f"获取积分排行榜成功, limit={limit}")
      return chart