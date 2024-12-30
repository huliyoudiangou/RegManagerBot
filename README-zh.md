# 🚀 本项目由优秀的 Gemini AI 助手指导完成！ 🤖

# 基于 Telegram Bot 的 Navidrome 和 Emby 用户管理系统

## 项目描述

本系统是一个强大而灵活的用户管理系统，旨在管理 Navidrome 和 Emby 媒体服务器的用户。它由一个 Telegram 机器人控制，允许你管理用户、生成邀请码、管理用户积分等。本项目使用 Python 构建，借助 pyTelegramBotAPI、sqlite 和 loguru。

## 项目功能

-   **用户管理：** 在 Navidrome 和 Emby 上创建、读取、更新和删除用户。
-   **邀请码系统：** 生成、验证和使用邀请码。
-   **用户积分管理：** 管理用户积分，包括增加、减少、设置和签到获得积分。
-   **Telegram 机器人控制：** 使用 Telegram 机器人管理整个系统。
-   **管理员和用户模式：** 不同的 Telegram 用户具有不同的权限。管理员可以管理所有用户，普通用户可以管理自己的信息。
-   **数据库支持：** 使用 SQLite 数据库存储用户数据、邀请码和用户积分。
-   **日志系统：** 使用 `loguru` 记录系统活动。

## 如何安装

你可以选择使用传统方法或者使用 Docker 和 Docker Compose 来安装本系统。

**传统方法**

1.  **克隆仓库:**
    ```bash
    git clone https://github.com/SenLief/RegManagerBot.git
    cd RegManagerBot
    ```
2.  **(可选) 创建虚拟环境:**
    ```bash
    python -m venv venv
    source venv/bin/activate # 在 Linux/macOS 上
    venv\Scripts\activate # 在 Windows 上
    ```
3.  **安装依赖包:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **配置 `.env` 文件：** 在项目根目录下创建一个 `.env` 文件，并添加以下配置。请将占位符替换为你的实际数据。
    ```
    DATABASE_URL="sqlite:///./data/db.sqlite3"
    TELEGRAM_BOT_TOKEN=your_telegram_bot_token
    ADMIN_TELEGRAM_IDS="123456789,987654321"
    NAVIDROME_API_URL=http://your_navidrome_url/api
    NAVIDROME_API_USERNAME=your_navidrome_username
    NAVIDROME_API_PASSWORD=your_navidrome_password
    EMBY_API_URL=http://your_emby_url/emby
    EMBY_API_KEY=your_emby_api_key
    INVITE_CODE_LENGTH=10
    INVITE_CODE_EXPIRATION_DAYS=14
    INVITE_CODE_SYSTEM_ENABLED=False
    INVITE_CODE_PRICE=100
    EXPIRED_DAYS=30
    WARNING_DAYS=3
    CLEAN_INTERVAL=2592000
    ENABLE_EXPIRED_USER_CLEAN=False
    ```
5.  **(可选) 创建 `regmangerbot.service` 文件，替换文件中的占位符：**
    ```
    [Unit]
    Description=RegManagerBot Telegram Bot
    After=network.target

    [Service]
    User=your_username  # 替换为你的用户名
    Group=your_username # 替换为你的用户名
    WorkingDirectory=/path/to/your/project  # 替换为你的项目路径
    ExecStart=/path/to/your/virtualenv/bin/python /path/to/your/project/main.py # 替换为你的虚拟环境路径和项目路径
    Restart=on-failure
    RestartSec=10

    [Install]
    WantedBy=multi-user.target
    ```
6.  **(可选) 启动服务：**
    ```bash
    sudo cp regmangerbot.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable regmangerbot.service
    sudo systemctl start regmangerbot.service
    ```

**Docker 和 Docker Compose 方法**

1.  **克隆仓库:**
    ```bash
    git clone https://github.com/SenLief/RegManagerBot.git
    cd RegManagerBot
    ```
2.  **配置 `.env` 文件：** 在项目根目录下创建一个 `.env` 文件，并添加以下配置，与传统方法一致
3.  **使用 Docker 镜像运行容器(请替换 /path/to/your/project 为你的项目路径):**
    ```bash
     docker run -d --name regmanagerbot \
    -v /path/to/your/project/data:/app/data \
    --env-file /path/to/your/project/.env \
     janzbff/regmanagerbot:latest
    ```

## 如何使用

1.  **运行应用程序：**
    -   **传统方法：** 运行 `python main.py`。
    -   **Docker 和 Docker Compose 方法：** 应用程序将在后台自动运行。
2.  **开始与 Telegram 机器人对话：** 使用你配置的 Telegram 机器人发送命令来管理系统。
3.  **管理员可用命令：**
    -   `/generate_code`：生成新的邀请码。
    -   `/invite`：查看所有邀请码。
    -   `/toggle_invite_code_system`：启用/禁用邀请码系统。
    -   `/set_score <telegram_id> <score>`：设置用户积分。
    -   `/get_score <telegram_id>` 或 `/score <telegram_id>`：查看用户积分。
    -   `/add_score <telegram_id> <score>`：为用户增加积分。
    -   `/reduce_score <telegram_id> <score>`：减少用户的积分。
    -   `/set_price <config_name> <price>`: 设置价格配置，例如 `/set_price INVITE_CODE_PRICE 150`
    -   `/userinfo <telegram_id>`： 通过 telegram id 获取用户信息。
    -   `/userinfo_by_username <username>`：通过用户名获取用户信息。
    -   `/stats`：获取注册用户统计信息。
4.  **普通用户可用命令：**
   -   `/start`： 获取用户信息和所有可用命令
    - `/register <username> <password>`: 注册用户 (需要提供用户名和密码).
    - `/register <username> <password> <invite_code>`: 使用邀请码注册用户 (需要提供用户名、密码和邀请码).
    -   `/info`： 获取用户信息
    -   `/use_code <username> <password> <invite_code>`： 使用邀请码
    -  `/deleteuser`：删除用户账户
    -   `/score`： 查看你的积分
    -   `/checkin`：签到获得积分
    -  `/buyinvite`： 购买邀请码
    -  `/reset_password`：重置密码
    -   `/give`： 赠送积分
    -  `/bind`：绑定账号
    - `/unbind`：解绑账号

## 如何贡献

我们欢迎所有对本项目的贡献。如果你想帮助改进系统，请：

1.  **Fork 本仓库。**
2.  **为你的功能或修复创建一个新的分支。**
3.  **提交你的更改。**
4.  **推送你的分支。**
5.  **创建一个 Pull Request。**

## 待办事项

-   添加对更多 Web 应用的支持。
-   为机器人逻辑添加更多测试。
-   添加更多功能，例如群组管理和媒体管理。
-   添加更强大、更灵活的用户权限系统。
-   为系统添加用户界面。