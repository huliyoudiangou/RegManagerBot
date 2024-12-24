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

    def __init__(self, code, is_used=False, user_id=None, create_time=None, expire_time=None, create_user_id=None, id=None):
        self.id = id
        self.code = code
        self.is_used = is_used
        self.user_id = user_id
        
        if isinstance(create_time, str):
            self.create_time = datetime.fromisoformat(create_time)
        else:
          self.create_time = create_time
        
        if isinstance(expire_time, str):
            self.expire_time = datetime.fromisoformat(expire_time)
        else:
          self.expire_time = expire_time

        self.create_user_id = create_user_id
        logger.debug(f"创建邀请码模型: id={self.id}, code={self.code}, create_user_id={self.create_user_id}")

    def save(self):
        """保存邀请码到数据库"""
        logger.info(f"保存邀请码到数据库: id={self.id}, code={self.code}, create_user_id={self.create_user_id}")
        conn = get_db_connection()
        cursor = conn.cursor()

        if self.id:
            # 更新
            cursor.execute(
                "UPDATE InviteCodes SET code = ?, is_used = ?, user_id = ?, create_time = ?, expire_time = ?, create_user_id = ? WHERE id = ?",
                (self.code, self.is_used, self.user_id, self.create_time, self.expire_time, self.create_user_id, self.id)
            )
            logger.debug(f"更新邀请码数据: id={self.id}, code={self.code}, create_user_id={self.create_user_id}")
        else:
            # 插入
            cursor.execute(
                "INSERT INTO InviteCodes (code, is_used, user_id, create_time, expire_time, create_user_id) VALUES (?, ?, ?, ?, ?, ?)",
                (self.code, self.is_used, self.user_id, self.create_time, self.expire_time, self.create_user_id)
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
            return InviteCode(row['code'], row['is_used'], row['user_id'], row['create_time'], row['expire_time'], row['create_user_id'], row['id'])
        else:
            logger.warning(f"邀请码不存在: code={code}")
            return None

    @staticmethod
    def generate_code(length=settings.INVITE_CODE_LENGTH, user_id=1):
      """生成邀请码"""
      logger.info(f"生成邀请码，长度为: {length}")
      chars = string.ascii_uppercase + string.digits
      code = ''.join(random.choice(chars) for _ in range(length))
      create_time = datetime.now()
      expire_time = create_time + timedelta(days=settings.INVITE_CODE_EXPIRATION_DAYS)

      invite_code = InviteCode(code=code, create_time=create_time, expire_time=expire_time, create_user_id=user_id)
      invite_code.save()
      logger.info(f"邀请码生成成功: code={code}")

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

      return [InviteCode(row['code'], row['is_used'], row['user_id'], row['create_time'], row['expire_time'], row['create_user_id'], row['id']) for row in rows]

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
        return f"<InviteCode id={self.id}, code={self.code}, is_used={self.is_used}, user_id={self.user_id}, create_time={self.create_time}, expire_time={self.expire_time}, create_user_id={self.create_user_id}>"