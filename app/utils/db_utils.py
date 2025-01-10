import sqlite3
import threading
from config import settings

# 需要安装的模块：无 (sqlite3 是 Python 内置模块)

db_lock = threading.Lock()
def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(settings.DATABASE_URL)
    conn.row_factory = sqlite3.Row  # 使查询结果可以像字典一样访问
    return conn

def close_db_connection(conn):
    """关闭数据库连接"""
    if conn:
        conn.close()

def create_tables():
    """创建数据库表"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 创建 Users 表
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
            expiration_date DATETIME, 
            last_sign_in_date DATETIME,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(telegram_id, service_type) 
        )
    """)

    # 创建 InviteCodes 表
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
            FOREIGN KEY (user_id) REFERENCES Users(telegram_id)
        )
    """)
    
    # 创建 RandomScoreEvents 表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS RandomScoreEvents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            create_user_id INTEGER NOT NULL,
            telegram_chat_id INTEGER NOT NULL,
            total_score INTEGER NOT NULL,
            participants_count INTEGER NOT NULL,
            score_list TEXT NOT NULL,
            score_result TEXT,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            end_time DATETIME,
            is_finished BOOLEAN DEFAULT FALSE
        )
    """)

    conn.commit()
    close_db_connection(conn)

import sqlite3
from config import settings

# ... (之前的 get_db_connection, close_db_connection, create_tables 函数) ...

def insert_data(table_name, data):
    """插入数据"""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        values = tuple(data.values())

        try:
            cursor.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})", values)
            conn.commit()
            return cursor.lastrowid  # 返回插入的行ID
        except sqlite3.Error as e:
            print(f"Error inserting data into {table_name}: {e}")
            return None
        finally:
            close_db_connection(conn)

def select_data(table_name, where_clause=None, order_by=None, where_values = None):
    """查询数据"""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = f"SELECT * FROM {table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"
        if order_by:
            query += f" ORDER BY {order_by}"

        try:
            if where_values:
                cursor.execute(query, tuple(where_values))
            else:
              cursor.execute(query)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"Error selecting data from {table_name}: {e}")
            return None
        finally:
            close_db_connection(conn)

def update_data(table_name, data, where_clause, where_values = None):
    """更新数据"""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()

        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        values = tuple(data.values())

        try:
            if where_values:
              cursor.execute(f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}", values + tuple(where_values))
            else:
              cursor.execute(f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}", values )
            conn.commit()
            return cursor.rowcount  # 返回更新的行数
        except sqlite3.Error as e:
            print(f"Error updating data in {table_name}: {e}")
            return None
        finally:
            close_db_connection(conn)

def delete_data(table_name, where_clause, where_values = None):
    """删除数据"""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            if where_values:
                cursor.execute(f"DELETE FROM {table_name} WHERE {where_clause}", tuple(where_values))
            else:
                cursor.execute(f"DELETE FROM {table_name} WHERE {where_clause}")
            conn.commit()
            return cursor.rowcount  # 返回删除的行数
        except sqlite3.Error as e:
            print(f"Error deleting data from {table_name}: {e}")
            return None
        finally:
            close_db_connection(conn)
        
# 示例用法 (可选)
if __name__ == "__main__":
    create_tables()