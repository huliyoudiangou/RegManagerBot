from app.utils.db_utils import get_db_connection, close_db_connection
from app.utils.logger import logger
from datetime import datetime

# 需要安装的模块：无

class User:
    """
    用户模型基类
    """

    def __init__(self, telegram_id, service_name, score=0, invite_code=None, id=None, last_sign_in_date=None):
        self.id = id
        self.telegram_id = telegram_id
        self.service_name = service_name
        self.score = score
        self.invite_code = invite_code
        
        if isinstance(last_sign_in_date, str):
            self.last_sign_in_date = datetime.fromisoformat(last_sign_in_date)
        else:
            self.last_sign_in_date = last_sign_in_date

        logger.debug(f"创建用户模型: id={self.id}, telegram_id={self.telegram_id}, service_name={self.service_name}, last_sign_in_date={self.last_sign_in_date}")

    def save(self):
        """保存用户信息到数据库"""
        logger.info(f"保存用户信息到数据库: id={self.id}, telegram_id={self.telegram_id}, service_name={self.service_name}, last_sign_in_date={self.last_sign_in_date}")
        conn = get_db_connection()
        cursor = conn.cursor()

        if self.id:
            # 更新
            cursor.execute(
                "UPDATE Users SET telegram_id = ?, service_name = ?, score = ?, invite_code = ?, last_sign_in_date = ? WHERE id = ?",
                (self.telegram_id, self.service_name, self.score, self.invite_code, self.last_sign_in_date, self.id)
            )
            logger.debug(f"更新用户数据: id={self.id}, telegram_id={self.telegram_id}, service_name={self.service_name}, last_sign_in_date={self.last_sign_in_date}")
        else:
            # 插入
            cursor.execute(
                "INSERT INTO Users (telegram_id, service_name, score, invite_code, last_sign_in_date) VALUES (?, ?, ?, ?, ?)",
                (self.telegram_id, self.service_name, self.score, self.invite_code, self.last_sign_in_date)
            )
            self.id = cursor.lastrowid
            logger.debug(f"插入用户数据: id={self.id}, telegram_id={self.telegram_id}, service_name={self.service_name}, last_sign_in_date={self.last_sign_in_date}")

        conn.commit()
        close_db_connection(conn)
        logger.info(f"用户信息保存成功: id={self.id}, telegram_id={self.telegram_id}, service_name={self.service_name}, last_sign_in_date={self.last_sign_in_date}")
        return self

    @staticmethod
    def get_by_telegram_id_and_service_name(telegram_id, service_name):
        """根据 Telegram ID 和服务名称查询用户"""
        logger.info(f"查询用户: telegram_id={telegram_id}, service_name={service_name}")
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM Users WHERE telegram_id = ? AND service_name = ?",
            (telegram_id, service_name)
        )
        row = cursor.fetchone()
        close_db_connection(conn)

        if row:
            logger.info(f"查询用户成功: telegram_id={telegram_id}, service_name={service_name}, id={row['id']}")
            return User(row['telegram_id'], row['service_name'], row['score'], row['invite_code'], row['id'], row['last_sign_in_date'])
        else:
            logger.warning(f"用户不存在: telegram_id={telegram_id}, service_name={service_name}")
            return None

    @staticmethod
    def get_by_id(user_id):
        """根据用户 ID 查询用户"""
        logger.info(f"查询用户: user_id={user_id}")
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        close_db_connection(conn)

        if row:
            logger.info(f"查询用户成功: user_id={user_id}, telegram_id={row['telegram_id']}")
            return User(row['telegram_id'], row['service_name'], row['score'], row['invite_code'], row['id'], row['last_sign_in_date'])
        else:
            logger.warning(f"用户不存在: user_id={user_id}")
            return None

    @staticmethod
    def get_all():
        """查询所有用户"""
        logger.info("查询所有用户")
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Users")
        rows = cursor.fetchall()
        close_db_connection(conn)

        logger.info(f"查询所有用户成功，共 {len(rows)} 个用户")
        return [User(row['telegram_id'], row['service_name'], row['score'], row['invite_code'], row['id'], row['last_sign_in_date']) for row in rows]

    def delete(self):
        """从数据库中删除用户"""
        logger.info(f"删除用户: id={self.id}, telegram_id={self.telegram_id}, service_name={self.service_name}")
        if self.id:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Users WHERE id = ?", (self.id,))
            conn.commit()
            close_db_connection(conn)
            logger.info(f"用户删除成功: id={self.id}, telegram_id={self.telegram_id}, service_name={self.service_name}")
            self.id = None  # 删除后将 id 设置为 None
        else:
            logger.warning(f"用户 id 为空，无法删除用户: telegram_id={self.telegram_id}, service_name={self.service_name}")

    def __str__(self):
        return f"<User id={self.id}, telegram_id={self.telegram_id}, service_name={self.service_name}, score={self.score}, invite_code={self.invite_code}>"

class NavidromeUser(User):
    """
    Navidrome 用户模型
    """

    def __init__(self, telegram_id, score=0, invite_code=None, id=None, navidrome_user_id=None, service_name='navidrome', last_sign_in_date=None):
        super().__init__(telegram_id, service_name, score, invite_code, id, last_sign_in_date)
        self.navidrome_user_id = navidrome_user_id
        logger.debug(f"创建 Navidrome 用户模型: id={self.id}, telegram_id={self.telegram_id}, navidrome_user_id={self.navidrome_user_id}, last_sign_in_date={self.last_sign_in_date}")

    def save(self):
        """保存用户信息到数据库"""
        logger.info(f"保存 Navidrome 用户信息到数据库: id={self.id}, telegram_id={self.telegram_id}, service_name={self.service_name}, navidrome_user_id={self.navidrome_user_id}, last_sign_in_date={self.last_sign_in_date}")
        conn = get_db_connection()
        cursor = conn.cursor()

        if self.id:
            # 更新
            cursor.execute(
                "UPDATE Users SET telegram_id = ?, service_name = ?, score = ?, invite_code = ?, navidrome_user_id = ?, last_sign_in_date = ? WHERE id = ?",
                (self.telegram_id, self.service_name, self.score, self.invite_code, self.navidrome_user_id, self.last_sign_in_date, self.id)
            )
            logger.debug(f"更新 Navidrome 用户数据: id={self.id}, telegram_id={self.telegram_id}, service_name={self.service_name}, navidrome_user_id={self.navidrome_user_id}, last_sign_in_date={self.last_sign_in_date}")
        else:
            # 插入
            cursor.execute(
                "INSERT INTO Users (telegram_id, service_name, score, invite_code, navidrome_user_id, last_sign_in_date) VALUES (?, ?, ?, ?, ?, ?)",
                (self.telegram_id, self.service_name, self.score, self.invite_code, self.navidrome_user_id, self.last_sign_in_date)
            )
            self.id = cursor.lastrowid
            logger.debug(f"插入 Navidrome 用户数据: id={self.id}, telegram_id={self.telegram_id}, service_name={self.service_name}, navidrome_user_id={self.navidrome_user_id}, last_sign_in_date={self.last_sign_in_date}")

        conn.commit()
        close_db_connection(conn)
        logger.info(f"Navidrome 用户信息保存成功: id={self.id}, telegram_id={self.telegram_id}, service_name={self.service_name}, navidrome_user_id={self.navidrome_user_id}, last_sign_in_date={self.last_sign_in_date}")
        return self

    @staticmethod
    def get_by_telegram_id_and_service_name(telegram_id, service_name):
        """根据 Telegram ID 和服务名称查询用户"""
        logger.info(f"查询 Navidrome 用户: telegram_id={telegram_id}, service_name={service_name}")
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM Users WHERE telegram_id = ? AND service_name = ?",
            (telegram_id, service_name)
        )
        row = cursor.fetchone()
        close_db_connection(conn)

        if row:
            logger.info(f"查询 Navidrome 用户成功: telegram_id={telegram_id}, service_name={service_name}, id={row['id']}")
            return NavidromeUser(row['telegram_id'], row['score'], row['invite_code'], row['id'], row['navidrome_user_id'], service_name = row['service_name'], last_sign_in_date = row['last_sign_in_date'])
        else:
            logger.warning(f"Navidrome 用户不存在: telegram_id={telegram_id}, service_name={service_name}")
            return None

    @staticmethod
    def get_by_id(user_id):
        """根据用户 ID 查询用户"""
        logger.info(f"查询 Navidrome 用户: user_id={user_id}")
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        close_db_connection(conn)

        if row:
            logger.info(f"查询 Navidrome 用户成功: user_id={user_id}, telegram_id={row['telegram_id']}")
            return NavidromeUser(row['telegram_id'], row['score'], row['invite_code'], row['id'], row['navidrome_user_id'], service_name = row['service_name'], last_sign_in_date = row['last_sign_in_date'])
        else:
            logger.warning(f"Navidrome 用户不存在: user_id={user_id}")
            return None

    @staticmethod
    def get_all():
        """查询所有用户"""
        logger.info("查询所有 Navidrome 用户")
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Users")
        rows = cursor.fetchall()
        close_db_connection(conn)

        logger.info(f"查询所有 Navidrome 用户成功, 共 {len(rows)} 个用户")
        return [NavidromeUser(row['telegram_id'], row['score'], row['invite_code'], row['id'], row['navidrome_user_id'], service_name = row['service_name'], last_sign_in_date = row['last_sign_in_date']) for row in rows]

    def __str__(self):
        return f"<NavidromeUser id={self.id}, telegram_id={self.telegram_id}, navidrome_user_id={self.navidrome_user_id}, score={self.score}, invite_code={self.invite_code}, last_sign_in_date={self.last_sign_in_date}>"

class EmbyUser(User):
    """
    Emby 用户模型 (预留)
    """

    def __init__(self, telegram_id, score=0, invite_code=None, id=None, emby_user_id=None):
        super().__init__(telegram_id, 'emby', score, invite_code, id)
        self.emby_user_id = emby_user_id
        # 你可以在这里添加更多 Emby 特有的属性
        logger.debug(f"创建 Emby 用户模型: id={self.id}, telegram_id={self.telegram_id}, emby_user_id={self.emby_user_id}")

    def __str__(self):
        return f"<EmbyUser id={self.id}, telegram_id={self.telegram_id}, emby_user_id={self.emby_user_id}, score={self.score}, invite_code={self.invite_code}>"