# 用户管理服务
from app.models import User, NavidromeUser
from app.utils.api_clients import navidrome_api_client
from app.utils.logger import logger
from config import settings
from app.utils.db_utils import insert_data, select_data, update_data, delete_data

# 需要安装的模块：无

class UserService:
    """
    用户服务
    """

    @staticmethod
    def register_user(telegram_id, service_name, username, password, email=None):
        """
        注册用户

        Args:
            telegram_id: Telegram ID
            service_name: 服务名称，例如 "navidrome"
            username: 用户名 (在对应web应用中的用户名)
            password: 密码 (在对应web应用中的密码)

        Returns:
            注册成功的用户对象，如果注册失败则返回 None
        """
        logger.info(f"开始注册用户: telegram_id={telegram_id}, service_name={service_name}, username={username}, password={password}")

        # 检查用户是否已存在
        user = NavidromeUser.get_by_telegram_id_and_service_name(telegram_id, service_name)
        if user:
            logger.warning(f"用户已存在: telegram_id={telegram_id}, service_name={service_name}")
            return user
        if email is None:
            email = ""
        # 在 Navidrome 中创建用户
        if service_name == "navidrome":
            user_data = {"userName": username, "password": password, "email": email}  # 假设邮箱为用户名@example.com
            result = navidrome_api_client.create_user(user_data)
            logger.info(f"Navidrome 用户创建结果: {result}")
            if result and result['status'] == 'success':
                navidrome_user_id = result['data']['id']
                logger.info(f"Navidrome 用户创建成功: navidrome_user_id={navidrome_user_id}")

                # 在本地数据库中创建用户
                user = NavidromeUser(telegram_id=telegram_id, service_name=service_name, navidrome_user_id=navidrome_user_id)
                user.save()
                logger.info(f"本地用户创建成功: user_id={user.id}, telegram_id={user.telegram_id}, service_name={user.service_name}, navidrome_user_id={user.navidrome_user_id}")
                return user
            else:
                logger.error(f"Navidrome 用户创建失败: {result}")
                return None
        else:
            logger.error(f"不支持的服务名称: {service_name}")
            return None
        
    @staticmethod
    def delete_user(user):
      """删除用户"""
      logger.info(f"开始删除用户: user_id={user.id}, telegram_id={user.telegram_id}, service_name={user.service_name}, navidrome_user_id={user.navidrome_user_id}")
      if user.service_name == "navidrome":
        # 删除 Navidrome 上的用户
        result = navidrome_api_client.delete_user(user.navidrome_user_id)
        if result and result['status'] == 'success':
          logger.info(f"Navidrome 用户删除成功: user_id={user.navidrome_user_id}")
          # 删除本地用户
          user.delete()
          logger.info(f"本地用户删除成功: user_id={user.id}")
          return True
        else:
          logger.error(f"Navidrome 用户删除失败: {result}")
          return False

    @staticmethod
    def get_user_by_telegram_id(telegram_id, service_name):
        """
        根据 Telegram ID 和服务名称查询用户

        Args:
            telegram_id: Telegram ID
            service_name: 服务名称

        Returns:
            User 对象，如果用户不存在则返回 None
        """
        logger.info(f"查询用户: telegram_id={telegram_id}, service_name={service_name}")
        user = NavidromeUser.get_by_telegram_id_and_service_name(telegram_id, service_name)
        logger.info(f"查询结果: {user}")
        if user:
          if service_name == 'navidrome':
            # 获取 Navidrome 用户信息
            navidrome_user_info = navidrome_api_client.get_user(user.navidrome_user_id)
            if navidrome_user_info and navidrome_user_info['status'] == 'success':
              logger.info(f"获取 Navidrome 用户信息成功: {navidrome_user_info}")
              user.navidrome_username = navidrome_user_info['data']['userName']
              return user
            else:
              logger.error(f"获取 Navidrome 用户信息失败: {navidrome_user_info}")
              return None
          else:
            logger.error(f"不支持的服务名称: {service_name}")
            return None
        else:
            logger.warning(f"用户不存在: telegram_id={telegram_id}, service_name={service_name}")
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
        logger.info(f"查询用户: user_id={user_id}")
        user = NavidromeUser.get_by_id(user_id)
        if user:
            logger.info(f"用户查询成功: user={user}")
            return user
        else:
            logger.warning(f"用户不存在: user_id={user_id}")
            return None
    
    @staticmethod
    def get_all_users():
      """获取所有用户"""
      logger.info("获取所有用户")
      users = NavidromeUser.get_all()
      if users:
        logger.info(f"获取所有用户成功: users={users}")
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
      logger.info(f"用户积分更新成功: user_id={user.id}, score={user.score}")
      return user