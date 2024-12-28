# 积分服务
from app.models import User
from app.utils.logger import logger
from app.services.user_service import UserService
from datetime import datetime, timedelta, date

# 需要安装的模块：无

class ScoreService:
    """
    积分服务
    """

    @staticmethod
    def get_user_score(user_id):
        """
        获取用户积分

        Args:
            user_id: 用户 ID

        Returns:
            用户积分，如果用户不存在则返回 None
        """
        logger.info(f"获取用户积分: user_id={user_id}")
        user = UserService.get_user_by_id(user_id)
        if user:
            logger.info(f"获取用户积分成功: user_id={user_id}, score={user.score}")
            return user.score
        else:
            logger.warning(f"用户不存在: user_id={user_id}")
            return None

    @staticmethod
    def add_score(user_id, score):
        """
        增加用户积分

        Args:
            user_id: 用户 ID
            score: 增加的积分

        Returns:
            更新后的用户对象，如果用户不存在则返回 None
        """
        logger.info(f"增加用户积分: user_id={user_id}, score={score}")
        user = UserService.get_user_by_id(user_id)
        if user:
            user.score += score
            user.save()
            logger.info(f"增加用户积分成功: user_id={user_id}, score={user.score}")
            return user
        else:
            logger.warning(f"用户不存在: user_id={user_id}")
            return None

    @staticmethod
    def reduce_score(user_id, score):
        """
        减少用户积分

        Args:
            user_id: 用户 ID
            score: 减少的积分

        Returns:
            更新后的用户对象，如果用户不存在则返回 None
        """
        logger.info(f"减少用户积分: user_id={user_id}, score={score}")
        user = UserService.get_user_by_id(user_id)
        if user:
            if user.score >= score:
                user.score -= score
                user.save()
                logger.info(f"减少用户积分成功: user_id={user_id}, score={user.score}")
                return user
            else:
                logger.warning(f"用户积分不足: user_id={user_id}, score={user.score}, required={score}")
                return None
        else:
            logger.warning(f"用户不存在: user_id={user_id}")
            return None
    
    @staticmethod
    def update_user_score(user_id, score):
        """
        设置用户积分

        Args:
            user_id: 用户 ID
            score: 设置的积分

        Returns:
            更新后的用户对象，如果用户不存在则返回 None
        """
        logger.info(f"设置用户积分: user_id={user_id}, score={score}")
        user = UserService.get_user_by_id(user_id)
        if user:
            user.score = score
            user.save()
            logger.info(f"设置用户积分成功: user_id={user_id}, score={user.score}")
            return user
        else:
            logger.warning(f"用户不存在: user_id={user_id}")
            return None

    @staticmethod
    def sign_in(user_id, max_score=10):
        """
        签到

        Args:
            user_id: 用户 ID
            max_score: 签到可获得的最大积分，默认为 10

        Returns:
            签到结果，如果签到成功则返回 True，如果用户不存在或已签到则返回 False
        """
        logger.info(f"用户签到: user_id={user_id}")
        user = UserService.get_user_by_id(user_id)
        if user:
            # 检查今天是否已签到
            last_sign_in_date = getattr(user, 'last_sign_in_date', None)
            if last_sign_in_date and last_sign_in_date.date() == date.today():
                logger.warning(f"用户今日已签到: user_id={user_id}")
                return False

            # 签到，增加随机积分
            import random
            sign_in_score = random.randint(1, max_score)  # 生成 1 到 max_score 之间的随机整数
            user.score += sign_in_score
            user.last_sign_in_date = datetime.now()
            user.save()
            logger.info(f"用户签到成功: user_id={user_id}, 获得积分={sign_in_score}, 总积分={user.score}, last_sign_in_date={user.last_sign_in_date}")
            return sign_in_score
        else:
            logger.warning(f"用户不存在: user_id={user_id}")
            return False