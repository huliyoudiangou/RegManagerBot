# 积分服务
from app.models import User
from app.utils.logger import logger
from app.services.user_service import UserService
from datetime import datetime, date
import pytz
import json
import random
from app.utils.db_utils import insert_data, select_data, update_data
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
        logger.debug(f"获取用户积分: user_id={user_id}")
        user = UserService.get_user_by_id(user_id)
        if user:
            logger.debug(f"获取用户积分成功: user_id={user_id}, score={user.score}")
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
        logger.debug(f"增加用户积分: user_id={user_id}, score={score}")
        user = UserService.get_user_by_id(user_id)
        if user:
            user.score += score
            user.save()
            logger.debug(f"增加用户积分成功: user_id={user_id}, score={user.score}")
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
        logger.debug(f"减少用户积分: user_id={user_id}, score={score}")
        user = UserService.get_user_by_id(user_id)
        if user:
            if user.score >= score:
                user.score -= score
                user.save()
                logger.debug(f"减少用户积分成功: user_id={user_id}, score={user.score}")
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
        logger.debug(f"设置用户积分: user_id={user_id}, score={score}")
        user = UserService.get_user_by_id(user_id)
        if user:
            user.score = score
            user.save()
            logger.debug(f"设置用户积分成功: user_id={user_id}, score={user.score}")
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
            签到结果，如果签到成功则返回 sign_in_score，如果用户不存在或已签到则返回 False
        """
        logger.debug(f"用户签到: user_id={user_id}")
        user = UserService.get_user_by_id(user_id)
        if user:
            # 检查今天是否已签到
            shanghai_tz = pytz.timezone('Asia/Shanghai')
            now_shanghai = datetime.now(shanghai_tz)
            
            last_sign_in_date = getattr(user, 'last_sign_in_date', None)
            if last_sign_in_date and last_sign_in_date.astimezone(shanghai_tz).date() == now_shanghai.date():
                logger.warning(f"用户今日已签到: user_id={user_id}")
                return False

            # 签到，增加随机积分
            import random
            sign_in_score = random.randint(1, max_score)  # 生成 1 到 max_score 之间的随机整数
            user.score += sign_in_score
            user.last_sign_in_date = now_shanghai
            user.save()
            logger.debug(f"用户签到成功: user_id={user_id}, 获得积分={sign_in_score}, 总积分={user.score}, 时间={now_shanghai}")
            return sign_in_score
        else:
            logger.warning(f"用户不存在: user_id={user_id}")
            return False
    
    @staticmethod
    def create_random_score_event(create_user_id, telegram_chat_id, total_score, participants_count):
      """创建随机积分活动"""
      logger.debug(f"创建随机积分活动，create_user_id={create_user_id}, telegram_chat_id={telegram_chat_id}, total_score={total_score}, participants_count={participants_count}")

      score_list = ScoreService._generate_random_scores(total_score=total_score, participants_count=participants_count)
      data = {
              "create_user_id": create_user_id,
               "telegram_chat_id": telegram_chat_id,
               "total_score": total_score,
               "participants_count": participants_count,
              "score_list": json.dumps(score_list),
            }
      row_id = insert_data("RandomScoreEvents", data)
      logger.debug(f"创建随机积分活动成功，id={row_id}")
      return row_id

    @staticmethod
    def _generate_random_scores(total_score, participants_count):
        """生成随机积分列表，使用二倍均值算法"""
        logger.debug(f"生成随机积分列表，total_score={total_score}, participants_count={participants_count}")
        if participants_count <= 0 or total_score <= 0 or participants_count > total_score:
            logger.warning("参与人数或者总积分必须大于0或总积分必须大于人数！")
            return []
        
        min_score = 1
        max_score = 2 * (total_score / participants_count)

        scores = []
        remaining_score = total_score
        for _ in range(participants_count - 1):
           score = random.randint(min_score, int(max_score))
           scores.append(score)
           remaining_score -= score
           if remaining_score <= 0:
                break

        # 如果还有剩余，则添加到最后一个
        if remaining_score > 0:
          scores.append(remaining_score)
        
        random.shuffle(scores)
        logger.debug(f"生成随机积分列表成功，scores={scores}")
        return scores
    
    @staticmethod
    def get_random_score_event(event_id):
        """根据id获取随机积分活动"""
        logger.debug(f"根据id获取随机积分活动，event_id={event_id}")
        query = f"id = ?"
        event_data = select_data("RandomScoreEvents", query, where_values = [event_id])
        if event_data:
           logger.debug(f"根据id获取随机积分活动成功，event_id={event_id}")
           return event_data[0]
        else:
           logger.warning(f"根据id获取随机积分活动失败，event_id={event_id}")
           return None

    @staticmethod
    def use_random_score(event_id, user_id, user_name):
        """使用随机积分"""
        logger.info(f"使用随机积分, event_id={event_id}, user_id={user_id}, user_name={user_name}")
        event_data = ScoreService.get_random_score_event(event_id)
        if event_data:
           score_list = json.loads(event_data['score_list'])
           if event_data['score_result']:
               score_result = json.loads(event_data['score_result'])
           else:
               score_result = []

           if any(item.get('user_id') == user_id for item in score_result):
              logger.warning(f"用户已经获取过随机积分, user_id={user_id}")
              return None
           
           if len(score_list) <= len(score_result):
              logger.warning(f"积分已经分发完毕")
              return None

           user_score_data = score_list[len(score_result)]
           user_score = user_score_data

           score_result.append({"user_id": user_id, 'user_name': user_name, 'score':user_score })
           
           data = {
            "score_result": json.dumps(score_result),
           }
           
           if len(score_list) == len(score_result):
            data['is_finished'] = True
            data['end_time'] = datetime.now()
            logger.debug(f"积分分发完成, 设置is_finished=True")

           update_data("RandomScoreEvents", data, f"id = {event_id}")
           
           user = UserService.get_user_by_telegram_id(user_id, 'navidrome')
           if user:
            ScoreService.add_score(user_id=user.id, score=user_score)
            logger.info(f"用户使用随机积分成功, user_id={user_id}, score={user_score}")
           return user_score
        else:
          logger.warning(f"未获取到活动信息, event_id={event_id}")
          return None
    
    @staticmethod
    def _generate_random_score(max_score=10):
        """生成随机积分"""
        logger.debug(f"生成随机积分, max_score={max_score}")
        score = random.randint(1, max_score)
        logger.debug(f"生成随机积分成功: score={score}")
        return score