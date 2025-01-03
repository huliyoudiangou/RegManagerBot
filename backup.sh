#!/bin/bash

# chmod +x backup.sh
# crontab -e
# 0 3 * * * /path/to/your/backup.sh

#!/bin/bash

# Define variables
SOURCE_DB_PATH="./data/data.db" # 你的源数据库文件路径
BACKUP_DIR="./backups"             # 备份文件目标目录
LOG_FILE="./logs/sqlite_backup.log"   # 日志文件路径
# BOT_TOKEN="xx"              # 替换为你的 Telegram Bot Token
# CHAT_ID="xx"                  # 替换为接收文件的 Chat ID

# 函数: 日志记录
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> $LOG_FILE
}

# 创建备份目录(如果不存在)
if [ ! -d "$BACKUP_DIR" ]; then
    mkdir -p "$BACKUP_DIR"
    if [ $? -ne 0 ]; then
        log_message "ERROR: Failed to create backup directory $BACKUP_DIR"
        exit 1
    fi
fi

# 定义备份文件名称, 带有时间戳
BACKUP_FILE="$BACKUP_DIR/database_backup_$(date +%Y%m%d%H%M%S).sqlite"

# 使用 SQLite3 执行热备份
if sqlite3 $SOURCE_DB_PATH ".backup $BACKUP_FILE"; then
    log_message "INFO: Backup created successfully at $BACKUP_FILE"
else
    log_message "ERROR: Backup failed for database $SOURCE_DB_PATH"
    exit 1
fi

# 确认备份文件存在性
if [ ! -f "$BACKUP_FILE" ]; then
    log_message "ERROR: Backup file $BACKUP_FILE does not exist"
    exit 1
fi

# 发送备份文件到 Telegram
response=$(curl -s -o /dev/null -w "%{http_code}" -F "chat_id=$CHAT_ID" -F "document=@$BACKUP_FILE" "https://api.telegram.org/bot$BOT_TOKEN/sendDocument")

if [ "$response" -eq 200 ]; then
    log_message "INFO: Backup file successfully sent to Telegram chat $CHAT_ID"
else
    log_message "ERROR: Failed to send backup file to Telegram, HTTP response code: $response"
    exit 1
fi

# Delete backup files older than 30 days
find "$BACKUP_DIR" -type f -name "*.sqlite" -mtime +30 -exec rm {} \;
if [ $? -eq 0 ]; then
    log_message "INFO: Old backup files older than 30 days have been deleted"
else
    log_message "ERROR: Failed to delete old backup files"
fi