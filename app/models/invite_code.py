import random
import string
from datetime import datetime, timedelta
from app.utils.db_utils import get_db_connection, close_db_connection
from config import settings
from app.utils.logger import logger

# 需要安装的模块：无

class InviteCode:
    """
    邀请码模型
    """

    def __init__(self, code, is_used=False, user_id=None, create_time=None, expire_days=None, create_user_id=None, type='invite', id=None):
        self.id = id
        self.code = code
        self.is_used = is_used
        self.user_id = user_id
        
        if isinstance(create_time, str):
            self.create_time = datetime.fromisoformat(create_time)
        else:
            self.create_time = create_time
        
        self.expire_days = expire_days  # 过期天数或续期天数
        self.create_user_id = create_user_id
        self.type = type  # 邀请码类型：invite（邀请码）或 renew（续期码）
        logger.debug(f"创建邀请码模型: id={self.id}, code={self.code}, type={self.type}, create_user_id={self.create_user_id}")

    def save(self):
        """保存邀请码到数据库"""
        logger.info(f"保存邀请码到数据库: id={self.id}, code={self.code}, type={self.type}, create_user_id={self.create_user_id}")
        conn = get_db_connection()
        cursor = conn.cursor()

        if self.id:
            # 更新
            cursor.execute(
                "UPDATE InviteCodes SET code=?, is_used=?, user_id=?, create_time=?, expire_days=?, create_user_id=?, type=? WHERE id=?",
                (self.code, self.is_used, self.user_id, self.create_time, self.expire_days, self.create_user_id, self.type, self.id)
            )
            logger.debug(f"更新邀请码数据: id={self.id}, code={self.code}, create_user_id={self.create_user_id}")
        else:
            # 插入
            cursor.execute(
                "INSERT INTO InviteCodes (code, is_used, user_id, create_time, expire_days, create_user_id, type) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (self.code, self.is_used, self.user_id, self.create_time, self.expire_days, self.create_user_id, self.type)
            )
            self.id = cursor.lastrowid
            logger.debug(f"插入邀请码数据: id={self.id}, code={self.code}, create_user_id={self.create_user_id}")

        conn.commit()
        close_db_connection(conn)
        logger.info(f"邀请码保存成功: id={self.id}, code={self.code}, create_user_id={self.create_user_id}")
        return self

    @staticmethod
    def get_by_code(code):
        """根据邀请码查询"""
        logger.info(f"查询邀请码: code={code}")
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM InviteCodes WHERE code = ?", (code,))
        row = cursor.fetchone()
        close_db_connection(conn)

        if row:
            logger.info(f"查询邀请码成功: code={code}, id={row['id']}")
            return InviteCode(row['code'], row['is_used'], row['user_id'], row['create_time'], row['expire_days'], row['create_user_id'], row['type'], row['id'])
        else:
            logger.warning(f"邀请码不存在: code={code}")
            return None

    @staticmethod
    def generate_code(length: int = settings.INVITE_CODE_LENGTH, user_id: int = 1, expire_days: int = settings.INVITE_CODE_EXPIRATION_DAYS, code_type: str = 'invite') -> 'InviteCode':
        """
        生成邀请码或续期码

        Args:
            length: 邀请码长度，默认为配置中的长度
            user_id: 创建用户的 ID，默认为 1
            expire_days: 过期天数或续期天数，默认为配置中的天数
            type: 邀请码类型，'invite' 表示邀请码，'renew' 表示续期码，默认为 'invite'

        Returns:
            生成的邀请码对象
        """
        logger.info(f"开始生成邀请码: 长度={length}, 用户ID={user_id}, 过期天数={expire_days}, 类型={type}")
        
        # 生成随机邀请码
        chars = string.ascii_uppercase + string.digits
        code = ''.join(random.choice(chars) for _ in range(length))
        create_time = datetime.now()

        # 创建邀请码对象
        invite_code = InviteCode(
            code=code,
            create_time=create_time,
            expire_days=expire_days,
            create_user_id=user_id,
            type=code_type
        )
        invite_code.save()
        logger.info(f"邀请码生成成功: 邀请码={code}, 类型={type}")

        return invite_code
    
    @staticmethod
    def get_all():
      """查询所有邀请码"""
      logger.info("查询所有邀请码")
      conn = get_db_connection()
      cursor = conn.cursor()

      cursor.execute("SELECT * FROM InviteCodes")
      rows = cursor.fetchall()
      close_db_connection(conn)
      logger.info(f"查询所有邀请码成功, 共 {len(rows)} 个邀请码")

      return [InviteCode(row['code'], row['is_used'], row['user_id'], row['create_time'], row['expire_days'], row['create_user_id'], row['type'], row['id']) for row in rows]

    @staticmethod
    def get_by_is_used(is_used):
        """根据邀请码使用状态查询"""
        logger.info(f"查询邀请码,使用状态：is_used={is_used}")
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM InviteCodes WHERE is_used = ?", (is_used,))
        rows = cursor.fetchall()
        close_db_connection(conn)
        if rows:
            logger.info(f"查询邀请码成功,使用状态：is_used={is_used}, count = {len(rows)}")
            return [InviteCode(row['code'], row['is_used'], row['user_id'], row['create_time'], row['expire_days'], row['create_user_id'], row['type'], row['id']) for row in rows]
        else:
            logger.warning(f"查询邀请码为空,使用状态：is_used={is_used}")
            return None
        
    def delete(self):
      """删除邀请码"""
      logger.info(f"删除邀请码: id={self.id}, code={self.code}")
      if self.id:
          conn = get_db_connection()
          cursor = conn.cursor()
          cursor.execute("DELETE FROM InviteCodes WHERE id = ?", (self.id,))
          conn.commit()
          close_db_connection(conn)
          logger.info(f"邀请码删除成功: id={self.id}, code={self.code}")
          self.id = None  # 删除后将 id 设置为 None
      else:
          logger.warning(f"邀请码id 为空, 无法删除")

    def __str__(self):
        return f"<InviteCode id={self.id}, code={self.code}, is_used={self.is_used}, user_id={self.user_id}, create_time={self.create_time}, expire_days={self.expire_days}, type={self.type}, create_user_id={self.create_user_id}>"