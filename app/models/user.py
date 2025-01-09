from datetime import datetime
from app.utils.db_utils import get_db_connection, close_db_connection
from app.utils.logger import logger
from config import settings

# 需要安装的模块：无
class User:
    """
    用户模型基类
    """

    def __init__(self, telegram_id, service_type, score=0, invite_code=None, id=None, last_sign_in_date=None, username=None, status='active', expiration_date=None):
        self.id = id
        self.telegram_id = telegram_id
        self.service_type = service_type
        self.score = score
        self.invite_code = invite_code
        self.username = username
        self.status = status  # 新增状态字段
        self.expiration_date = expiration_date  # 新增过期时间字段
        
        if isinstance(last_sign_in_date, str):
            self.last_sign_in_date = datetime.fromisoformat(last_sign_in_date)
        else:
            self.last_sign_in_date = last_sign_in_date
        logger.debug(f"创建用户模型: id={self.id}, telegram_id={self.telegram_id}, service_type={self.service_type}")

    def save(self):
        """保存用户信息到数据库"""
        logger.debug(f"保存用户信息到数据库: id={self.id}, telegram_id={self.telegram_id}, service_type={self.service_type}")
        conn = get_db_connection()
        cursor = conn.cursor()

        if self.id:
            # 更新
            cursor.execute(
                "UPDATE Users SET telegram_id = ?, service_type = ?, score = ?, invite_code = ?, last_sign_in_date = ?, username = ?, status = ?, expiration_date = ? WHERE id = ?",
                (self.telegram_id, self.service_type, self.score, self.invite_code, self.last_sign_in_date, self.username, self.status, self.expiration_date, self.id)
            )
            logger.debug(f"更新用户数据: id={self.id}, telegram_id={self.telegram_id}, service_type={self.service_type}")
        else:
            # 插入
            cursor.execute(
                "INSERT INTO Users (telegram_id, service_type, score, invite_code, last_sign_in_date, username, status, expiration_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (self.telegram_id, self.service_type, self.score, self.invite_code, self.last_sign_in_date, self.username, self.status, self.expiration_date)
            )
            self.id = cursor.lastrowid
            logger.debug(f"插入用户数据: id={self.id}, telegram_id={self.telegram_id}, service_type={self.service_type}")

        conn.commit()
        close_db_connection(conn)
        logger.debug(f"用户信息保存成功: id={self.id}, telegram_id={self.telegram_id}, service_type={self.service_type}")
        return self

    @staticmethod
    def get_by_telegram_id_and_service_type(telegram_id, service_type=None):
        """根据 Telegram ID 和服务名称查询用户"""
        logger.debug(f"查询用户: telegram_id={telegram_id}, service_type={service_type}")
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM Users WHERE telegram_id = ? AND service_type = ?",
            (telegram_id, service_type)
        )
        row = cursor.fetchone()
        close_db_connection(conn)

        if row:
            logger.debug(f"查询用户成功: telegram_id={telegram_id}, service_type={service_type}, id={row['id']}")
            return User(row['telegram_id'], row['service_type'], row['score'], row['invite_code'], row['id'], row['last_sign_in_date'], row['username'], row['status'], row['expiration_date'])
        else:
            logger.warning(f"用户不存在: telegram_id={telegram_id}, service_type={service_type}")
            return None

    @staticmethod
    def get_by_id(user_id):
        """根据用户 ID 查询用户"""
        logger.debug(f"查询用户: user_id={user_id}")
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        close_db_connection(conn)

        if row:
            logger.debug(f"查询用户成功: user_id={user_id}, telegram_id={row['telegram_id']}")
            return User(row['telegram_id'], row['service_type'], row['score'], row['invite_code'], row['id'], row['last_sign_in_date'], row['username'], row['status'], row['expiration_date'])
        else:
            logger.warning(f"用户不存在: user_id={user_id}")
            return None

    @staticmethod
    def get_all():
        """查询所有用户"""
        logger.debug("查询所有用户")
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Users")
        rows = cursor.fetchall()
        close_db_connection(conn)

        logger.debug(f"查询所有用户成功，共 {len(rows)} 个用户")
        return [User(row['telegram_id'], row['service_type'], row['score'], row['invite_code'], row['id'], row['last_sign_in_date'], row['username'], row['status'], row['expiration_date']) for row in rows]

    def delete(self):
        """从数据库中删除用户"""
        logger.debug(f"删除用户: id={self.id}, telegram_id={self.telegram_id}, service_type={self.service_type}")
        if self.id:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Users WHERE id = ?", (self.id,))
            conn.commit()
            close_db_connection(conn)
            logger.debug(f"用户删除成功: id={self.id}, telegram_id={self.telegram_id}, service_type={self.service_type}")
            self.id = None  # 删除后将 id 设置为 None
        else:
            logger.warning(f"用户 id 为空，无法删除用户: telegram_id={self.telegram_id}, service_type={self.service_type}")

    def __str__(self):
        return f"<User id={self.id}, telegram_id={self.telegram_id}, service_type={self.service_type}, score={self.score}, invite_code={self.invite_code}, last_sign_in_date={self.last_sign_in_date}, username={self.username}, status={self.status}, expiration_date={self.expiration_date}>"

class ServiceUser(User):
    """
    {service_type} 用户模型
    """

    def __init__(self, telegram_id, score=0, invite_code=None, id=None, service_user_id=None, last_sign_in_date=None, service_type='navidrome', username=None, status='active', expiration_date=None):
        super().__init__(telegram_id, service_type, score, invite_code, id, last_sign_in_date, username, status, expiration_date)
        self.service_user_id = service_user_id
        logger.debug(f"创建 {service_type} 用户模型: id={self.id}, telegram_id={self.telegram_id}, service_user_id={self.service_user_id}")

    def save(self):
        """保存用户信息到数据库"""
        logger.debug(f"保存 {self.service_type} 用户信息到数据库: id={self.id}, telegram_id={self.telegram_id}, service_type={self.service_type}, service_user_id={self.service_user_id}")
        conn = get_db_connection()
        cursor = conn.cursor()

        if self.id:
            # 更新
            cursor.execute(
                "UPDATE Users SET telegram_id = ?, service_type = ?, score = ?, invite_code = ?, service_user_id = ?, last_sign_in_date = ?, username = ?, status = ?, expiration_date = ? WHERE id = ?",
                (self.telegram_id, self.service_type, self.score, self.invite_code, self.service_user_id, self.last_sign_in_date, self.username, self.status, self.expiration_date, self.id)
            )
            logger.debug(f"更新 {self.service_type} 用户数据: id={self.id}, telegram_id={self.telegram_id}, service_type={self.service_type}, service_user_id={self.service_user_id}")
        else:
            # 插入
            cursor.execute(
                "INSERT INTO Users (telegram_id, service_type, score, invite_code, service_user_id, last_sign_in_date, username, status, expiration_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (self.telegram_id, self.service_type, self.score, self.invite_code, self.service_user_id, self.last_sign_in_date, self.username, self.status, self.expiration_date)
            )
            self.id = cursor.lastrowid
            logger.debug(f"插入 {self.service_type} 用户数据: id={self.id}, telegram_id={self.telegram_id}, service_type={self.service_type}, service_user_id={self.service_user_id}")

        conn.commit()
        close_db_connection(conn)
        logger.debug(f"{self.service_type} 用户信息保存成功: id={self.id}, telegram_id={self.telegram_id}, service_type={self.service_type}, service_user_id={self.service_user_id}")
        return self

    @staticmethod
    def get_by_telegram_id_and_service_type(telegram_id, service_type=None):
        """根据 Telegram ID 和服务名称查询用户"""
        service_type = service_type if service_type is not None else settings.SERVICE_TYPE
        logger.debug(f"查询 {service_type} 用户: telegram_id={telegram_id}, service_type={service_type}")
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM Users WHERE telegram_id = ? AND service_type = ?",
            (telegram_id, service_type)
        )
        row = cursor.fetchone()
        close_db_connection(conn)

        if row:
           logger.debug(f"查询 {service_type} 用户成功: telegram_id={telegram_id}, service_type={service_type}, id={row['id']}")
           return ServiceUser(row['telegram_id'], row['score'], row['invite_code'], row['id'], row['service_user_id'], row['last_sign_in_date'], row['service_type'], row['username'], row['status'], row['expiration_date'])
        else:
           logger.warning(f"{service_type} 用户不存在: telegram_id={telegram_id}, service_type={service_type}")
           return None

    @staticmethod
    def get_by_id(user_id, service_type=None):
        """根据用户 ID 查询用户"""
        service_type = service_type if service_type is not None else settings.SERVICE_TYPE
        logger.debug(f"查询 {service_type} 用户: user_id={user_id}")
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        close_db_connection(conn)

        if row:
            logger.debug(f"查询 {service_type} 用户成功: user_id={user_id}, telegram_id={row['telegram_id']}")
            return ServiceUser(row['telegram_id'], row['score'], row['invite_code'], row['id'], row['service_user_id'], row['last_sign_in_date'], row['service_type'], row['username'], row['status'], row['expiration_date'])
        else:
            logger.warning(f"{service_type} 用户不存在: user_id={user_id}")
            return None
    
    @staticmethod
    def get_by_service_id(user_id, service_type=None):
        """根据用户 ID 查询用户"""
        service_type = service_type if service_type is not None else settings.SERVICE_TYPE
        logger.debug(f"查询 {service_type} 用户: user_id={user_id}")
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Users WHERE service_user_id = ?", (user_id,))
        row = cursor.fetchone()
        close_db_connection(conn)

        if row:
            logger.debug(f"查询 {service_type} 用户成功: user_id={user_id}, telegram_id={row['telegram_id']}")
            return ServiceUser(row['telegram_id'], row['score'], row['invite_code'], row['id'], row['service_user_id'], row['last_sign_in_date'], row['service_type'], row['username'], row['status'], row['expiration_date'])
        else:
            logger.warning(f"{service_type} 用户不存在: user_id={user_id}")
            return None

    @staticmethod
    def get_by_username(username, service_type=None):
        """根据 {service_type} 用户名查询用户"""
        service_type = service_type if service_type is not None else settings.SERVICE_TYPE
        logger.debug(f"根据 {service_type} 用户名查询用户: username={username}")
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Users WHERE username = ?", (username,))
        row = cursor.fetchone()
        close_db_connection(conn)

        if row:
            logger.debug(f"根据 {service_type} 用户名查询用户成功: username={username}, telegram_id={row['telegram_id']},id={row['id']}")
            return ServiceUser(row['telegram_id'], row['score'], row['invite_code'], row['id'], row['service_user_id'], row['last_sign_in_date'], row['service_type'], row['username'], row['status'], row['expiration_date'])
        else:
           logger.warning(f"{service_type} 用户不存在: username={username}")
           return None
    
    @staticmethod
    def get_all(service_type=None):
        """查询所有用户"""
        service_type = service_type if service_type is not None else settings.SERVICE_TYPE
        logger.debug("查询所有 {service_type} 用户")
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Users")
        rows = cursor.fetchall()
        close_db_connection(conn)

        logger.debug(f"查询所有 {service_type} 用户成功, 共 {len(rows)} 个用户")
        return [ServiceUser(row['telegram_id'], row['score'], row['invite_code'], row['id'], row['service_user_id'], row['last_sign_in_date'], row['service_type'], row['username'], row['status'], row['expiration_date']) for row in rows]

    @staticmethod
    def update_username(telegram_id, new_username, service_type=None):
        """
        修改 {service_type} 用户名
        Args:
          new_username: 新的用户名
        Returns:
          修改后的 ServiceUser对象
        """
        service_type = service_type if service_type is not None else settings.SERVICE_TYPE
        logger.debug(f"修改 {service_type} 用户名: new_username={new_username}")
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE Users SET username = ? WHERE telegram_id = ? AND service_type = ?", (new_username, telegram_id, service_type))
        conn.commit()
        # 获取更新后的数据
        cursor.execute(
            "SELECT * FROM Users WHERE telegram_id = ? AND service_type = ?",
            (telegram_id, service_type)
        )
        row = cursor.fetchone()
        close_db_connection(conn)
        if row:
          logger.debug(f"修改 {service_type} 用户名成功, 返回新的ServiceUser对象: new_username={new_username}, telegram_id={telegram_id}, service_type={service_type}, id={row['id']}")
          return ServiceUser(row['telegram_id'], row['score'], row['invite_code'], row['id'], row['service_user_id'], service_type = row['service_type'])
        else:
          logger.error(f"修改 {service_type} 用户名失败: new_username={new_username}, telegram_id={telegram_id}, service_type={service_type}")
          return None
    
    def __str__(self):
        return f"<ServiceUser id={self.id}, telegram_id={self.telegram_id}, service_user_id={self.service_user_id}, score={self.score}, invite_code={self.invite_code}, last_sign_in_date={self.last_sign_in_date}, username={self.username}, status={self.status}, expiration_date={self.expiration_date}>"