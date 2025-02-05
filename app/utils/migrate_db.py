import sqlite3
import os


def migrate_database(db_path):
    # 连接到现有数据库
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # 第一步：重命名旧的 Users 表
    cursor.execute("ALTER TABLE Users RENAME TO Users_old")

    # 第二步：创建新的 Users 表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            service_type TEXT NOT NULL,
            username TEXT,
            service_user_id TEXT,
            score INTEGER DEFAULT 0,
            invite_code TEXT,
            service_name TEXT,
            status TEXT DEFAULT 'active',
            expiration_date DATETIME DEFAULT NULL,
            last_sign_in_date DATETIME,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(telegram_id, service_type)
        )
    """)

    # 第三步：将旧的 Users 表的数据复制到新的表中
    cursor.execute("""
        INSERT INTO Users (
            id, telegram_id, service_type, username,
            service_user_id, score, invite_code,
            service_name, status, expiration_date, last_sign_in_date
        )
        SELECT
            id, telegram_id, 'navidrome', username,  -- 设置默认值为 'navidrome'
            navidrome_user_id, score, invite_code,
            service_name, 'active', NULL, last_sign_in_date  -- 设置 expiration_date 为 NULL
        FROM Users_old
    """)

    # 第四步：删除旧的 Users 表
    cursor.execute("DROP TABLE Users_old")

    # 重命名 InviteCodes 表的旧版本
    cursor.execute("ALTER TABLE InviteCodes RENAME TO InviteCodes_old")

    # 创建新的 InviteCodes 表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS InviteCodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            is_used BOOLEAN DEFAULT FALSE,
            user_id INTEGER,
            type TEXT NOT NULL CHECK(type IN ('invite', 'renew')),
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            expire_days INTEGER NOT NULL,
            expire_time DATETIME,
            create_user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES Users(id)
        )
    """)

    # 将旧 InviteCodes 表的数据迁移到新的表中，并设置默认值
    cursor.execute("""
        INSERT INTO InviteCodes (
            id, code, is_used, user_id, type,
            expire_days, create_time, expire_time, create_user_id
        )
        SELECT
            id, code, is_used, user_id, 'invite', -- 分配默认值
            30, -- 设定默认的过期期限天数
            create_time, expire_time, create_user_id
        FROM InviteCodes_old
    """)

    # 删除旧的 InviteCodes 表
    cursor.execute("DROP TABLE InviteCodes_old")

    # 提交更改并关闭连接
    connection.commit()
    connection.close()


# 调用迁移函数
current_dir = os.path.dirname(__file__)
db_path = os.path.join(current_dir, '../../data/data.db')
db_path = os.path.abspath(db_path)
migrate_database(db_path)

if __name__ == 'main':
    current_dir = os.path.dirname(__file__)
    db_path = os.path.join(current_dir, '../../data/data.db')
    db_path = os.path.abspath(db_path)
    migrate_database(db_path)
