# 邀请码服务层
from app.models import InviteCode
from app.utils.logger import logger
from config import settings
from datetime import datetime, timedelta
from typing import Optional
from app.models import User, ServiceUser
# 需要安装的模块：无

class InviteCodeService:
    """
    邀请码服务
    """

    @staticmethod
    def generate_invite_code(create_user_id: int, length: int = settings.INVITE_CODE_LENGTH, expire_days: int = settings.INVITE_CODE_EXPIRATION_DAYS, code_type: str = 'invite') -> Optional[InviteCode]:
        """
        生成邀请码或续期码

        Args:
            create_user_id: 创建邀请码的用户 telegram_id
            length: 邀请码长度，默认为 settings.INVITE_CODE_LENGTH
            expire_days: 邀请码有效天数或续期天数，默认为 settings.INVITE_CODE_EXPIRATION_DAYS
            code_type: 邀请码类型，'invite' 表示邀请码，'renew' 表示续期码，默认为 'invite'

        Returns:
            生成的邀请码对象，如果生成失败则返回 None
        """
        logger.debug(f"开始生成邀请码: create_user_id={create_user_id}, length={length}, expire_days={expire_days}, code_type={code_type}")
        
        # 检查 code_type 是否合法
        if code_type not in ['invite', 'renew']:
            logger.error(f"无效的邀请码类型: {code_type}")
            return None
        if code_type == 'invite':
            # 生成邀请码
            invite_code = InviteCode.generate_code(length=length, user_id=create_user_id, code_type=code_type, expire_days=expire_days)
        
        if invite_code:
            logger.debug(f"邀请码生成成功: invite_code={invite_code.code}")
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
        logger.debug(f"查询邀请码: code={code}")
        invite_code = InviteCode.get_by_code(code)
        if invite_code:
            logger.debug(f"邀请码查询成功: invite_code={invite_code}")
            return invite_code
        else:
            logger.warning(f"邀请码不存在: code={code}")
            return None

    @staticmethod
    def use_invite_code(code: str, user_id: int) -> bool:
        """
        使用邀请码

        Args:
            code: 邀请码
            user_id: 使用邀请码的用户 ID

        Returns:
            True 如果使用成功，否则返回 False
        """
        logger.debug(f"开始使用邀请码: code={code}, user_id={user_id}")
        invite_code = InviteCode.get_by_code(code)
        if invite_code:
            if invite_code.is_used:
                logger.warning(f"邀请码已被使用: code={code}")
                return False

            # 根据邀请码类型处理
            if invite_code.type == 'invite':
                # 计算过期时间
                expire_time = invite_code.create_time + timedelta(days=invite_code.expire_days)
                if expire_time < datetime.now():
                    logger.warning(f"邀请码已过期: code={code}")
                    return False
                # 处理邀请码逻辑
                invite_code.is_used = True
                invite_code.user_id = user_id
                invite_code.save()
                logger.debug(f"邀请码使用成功: code={code}, user_id={user_id}")
                return True
            elif invite_code.type == 'renew':
                # 处理续期码逻辑
                service_user = ServiceUser.get_by_telegram_id_and_service_type(user_id)
                if service_user:
                    # 更新用户的过期时间
                    if service_user.expiration_date:
                        new_expiration_date = service_user.expiration_date + timedelta(days=invite_code.expire_days)
                    else:
                        new_expiration_date = datetime.now() + timedelta(days=invite_code.expire_days)
                    service_user.expiration_date = new_expiration_date
                    service_user.save()
                    invite_code.is_used = True
                    invite_code.user_id = user_id
                    invite_code.save()
                    logger.debug(f"续期码使用成功: code={code}, user_id={user_id}, 新过期时间={new_expiration_date}")
                    return True
                else:
                    logger.warning(f"用户不存在: user_id={user_id}")
                    return False
            else:
                logger.error(f"未知的邀请码类型: type={invite_code.type}")
                return False
        else:
            logger.warning(f"邀请码不存在: code={code}")
            return False

    @staticmethod
    def get_all_invite_codes(code_type: str = None, is_used: bool = None):
        """
        获取所有邀请码，支持根据 code_type 和 is_used 筛选

        Args:
            code_type: 邀请码类型，'invite' 或 'renew'，默认为 None（不筛选）
            is_used: 是否使用，True 或 False，默认为 None（不筛选）

        Returns:
            符合条件的邀请码列表，如果获取失败则返回 None
        """
        logger.debug(f"获取所有邀请码: code_type={code_type}, is_used={is_used}")
        invite_codes = InviteCode.get_all()
        if invite_codes:
            # 根据 code_type 筛选
            if code_type:
                invite_codes = [code for code in invite_codes if code.type == code_type]
            # 根据 is_used 筛选
            if is_used is not None:
                invite_codes = [code for code in invite_codes if code.is_used == is_used]
            logger.debug(f"获取所有邀请码成功: invite_codes={invite_codes}")
            return invite_codes
        else:
            logger.warning("获取所有邀请码失败")
            return None
      
    @staticmethod
    def delete_invite_code(invite_code):
      """删除邀请码"""
      logger.debug(f"删除邀请码: invite_code={invite_code}")
      invite_code.delete()
      logger.debug(f"邀请码删除成功: invite_code={invite_code}")
      return True