# 邀请码服务层
from app.models import InviteCode
from app.utils.logger import logger
from app.services.user_service import UserService
from config import settings
from datetime import datetime, timedelta

# 需要安装的模块：无

class InviteCodeService:
    """
    邀请码服务
    """

    @staticmethod
    def generate_invite_code(create_user_id, length=settings.INVITE_CODE_LENGTH, expire_days=settings.INVITE_CODE_EXPIRATION_DAYS):
        """
        生成邀请码

        Args:
            create_user_id: 创建邀请码的用户 telegram_id
            length: 邀请码长度，默认为 settings.INVITE_CODE_LENGTH
            expire_days: 邀请码有效天数，默认为 settings.INVITE_CODE_EXPIRATION_DAYS

        Returns:
            生成的邀请码对象，如果生成失败则返回 None
        """
        logger.info(f"开始生成邀请码: create_user_id={create_user_id}, length={length}, expire_days={expire_days}")

        invite_code = InviteCode.generate_code(length=length, user_id=create_user_id)

        if invite_code:
            logger.info(f"邀请码生成成功: invite_code={invite_code.code}")
            return invite_code
        else:
            logger.error("邀请码生成失败")
            return None

    @staticmethod
    def get_invite_code(code):
        """
        根据邀请码查询邀请码信息

        Args:
            code: 邀请码

        Returns:
            邀请码对象，如果邀请码不存在则返回 None
        """
        logger.info(f"查询邀请码: code={code}")
        invite_code = InviteCode.get_by_code(code)
        if invite_code:
            logger.info(f"邀请码查询成功: invite_code={invite_code}")
            return invite_code
        else:
            logger.warning(f"邀请码不存在: code={code}")
            return None

    @staticmethod
    def use_invite_code(code, user_id):
        """
        使用邀请码

        Args:
            code: 邀请码
            user_id: 使用邀请码的用户 ID

        Returns:
            True 如果使用成功，否则返回 False
        """
        logger.info(f"开始使用邀请码: code={code}, user_id={user_id}")
        invite_code = InviteCode.get_by_code(code)
        if invite_code:
            if invite_code.is_used:
                logger.warning(f"邀请码已被使用: code={code}")
                return False
            if invite_code.expire_time < datetime.now():
                logger.warning(f"邀请码已过期: code={code}")
                return False

            invite_code.is_used = True
            invite_code.user_id = user_id
            invite_code.save()
            logger.info(f"邀请码使用成功: code={code}, user_id={user_id}")
            return True
        else:
            logger.warning(f"邀请码不存在: code={code}")
            return False

    @staticmethod
    def get_all_invite_codes():
        """获取所有邀请码"""
        logger.info("获取所有邀请码")
        invite_codes = InviteCode.get_all()
        if invite_codes:
          logger.info(f"获取所有邀请码成功: invite_codes={invite_codes}")
          return invite_codes
        else:
          logger.warning("获取所有邀请码失败")
          return None

    @staticmethod
    def delete_invite_code(invite_code):
      """删除邀请码"""
      logger.info(f"删除邀请码: invite_code={invite_code}")
      invite_code.delete()
      logger.info(f"邀请码删除成功: invite_code={invite_code}")
      return True