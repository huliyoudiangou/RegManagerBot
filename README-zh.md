# 🚀 本项目由优秀的 Gemini AI 助手和Deeepseek V3指导完成！ 🤖

# 基于 Telegram Bot 的 Navidrome、Emby、Audiobookshelf 等无网页注册功能的用户管理系统。

## 项目描述

本项目主要是是为一些自建服务提供基于Telegram Bot的用户管理，例如像Navidrome、Emby、Audiobookshelf等服务提供注册、删除、封禁、激活等，并基于Bot的本地功能实现积分和邀请码、续期码功能。

## 项目特点

-   **多服务支持：** 支持 Navidrome、Emby、Audiobookshelf 等自建服务。已抽象接口，可以自由对接其他服务。
-   **用户管理：** 为自建服务提供注册、删除、封禁、重置用户名和密码等功能。
-   **注册模板：**  为注册用户提供注册模板，使其注册的用户具有和模板一样的权限。
-   **邀请码系统：** 生成、验证和使用邀请码以及续期码。
-   **用户积分管理：** 管理用户积分，包括增加、减少、设置和签到获得积分。
-   **管理员和用户模式：** 不同的 Telegram 用户具有不同的权限。管理员可以管理所有用户，普通用户可以管理自己的信息。
-   **状态管理：**  用户状态包括正常、封禁、过期等状态，邀请注册系统开启和管理等。
-   **娱乐系统：** 获取积分，发送随机积分红包等。

## 工作原理

系统基于后端服务的ID和后端服务应用利用 API 进行交互，除用户管理外，其他功能都是基于Bot的本地功能实现，所以不会对后端服务造成压力。

## 功能简介

### 用户管理

-   **注册用户：** 用户可以注册到后端服务，并设置用户名和密码。
-   **删除用户：** 用户可以删除自己的账户，管理员可以删除任何用户(目前采用封禁模式)。
-   **封禁用户：** 管理员可以封禁用户，封禁后用户将无法使用服务(可选是否封禁后端服务)。
-   **重置用户名和密码：** 用户可以重置自己的用户名和密码。
-   **用户状态管理：** 用户可以查看自己的状态，管理员可以管理用户状态。

### 邀请码系统

-   **生成邀请码：** 管理员可以生成邀请码/续期码，普通用户可以购买邀请码。
-   **验证邀请码：** 系统会验证邀请码/续期码的有效性。
-   **使用邀请码：** 用户可以使用邀请码注册，续期码续期。

### 用户积分管理

-   **增加积分：** 管理员可以增加用户的积分。
-   **减少积分：** 管理员可以减少用户的积分。
-   **设置积分：** 管理员可以设置用户的积分。
-   **赠送积分：** 用户可以赠送积分给其他注册用户。
-   **签到获得积分：** 用户可以签到获得积分。
-   **积分红包：** 用户可以发送积分红包。

### 注册模板

> 在设计之初，一直在考虑不同的服务会有不同的权限设计，注册用户的权限有些默认并不友好，如果自己实现权限的控制，那无疑增加了很多的工作量，在看Emby文档时，受到Emby注册模式的启发，可以先由管理员注册一个模板用户，然后注册用户时，复制模板用户的权限，这样注册用户的权限就和模板用户一样了。

1. 在服务上新建一个模板用户，并设置好权限。
2. 在`.env`中设置模板用户的ID。
3. 注册用户时，会复制模板用户的权限用于新用户的权限。

### 日志系统

-   **记录系统活动：** 使用 `loguru` 记录系统活动。


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
4.  **配置 `.env` 文件：** 在项目根目录下创建一个 `.env` 文件或者复制`.env.example`文件，并添加以下配置。请将占位符替换为你的实际数据。
    ```
    DATABASE_URL="./data/data.db" # 数据库地址
    TELEGRAM_BOT_TOKEN="xxxxxxQzNiZnsqeazgTNg" # Telegram Bot Token
    WEBHOOK_URL="" # http://0.0.0.0:7000 or https://domain.com
    SERVICE_TYPE="emby" # navidrome|emby|audiobookshelf
    ADMIN_TELEGRAM_IDS="xxxx" # Telegram IDs, 23423423,34344234,2342343

    # Navidrome 配置
    NAVIDROME_API_URL="http://172.18.96.1:4533"
    NAVIDROME_API_USERNAME=xxxx # 需具有服务的管理员权限
    NAVIDROME_API_PASSWORD=xxxx

    # Emby 配置
    EMBY_API_URL="http://172.18.96.1:8096"  # Emby API 地址
    EMBY_API_KEY="2b04b0173xxxx929"  # Emby API 密钥 
    EMBY_API_USERNAME=xxx  # Navidrome API 用户名 【首选密钥登录】
    EMBY_API_PASSWORD=xxx  # Navidrome API 密码
    EMBY_COPY_FROM_ID="xxxxx" # 权限模板ID

    # Audiobookshelf 配置
    AUDIOBOOKSHELF_API_URL="http://172.18.96.1:13378"
    AUDIOBOOKSHELF_API_KEY=""  # Audiobookshelf API 密钥
    AUDIOBOOKSHELF_API_USERNAME=xxx  # Audiobookshelf API 用户名 首选密钥登录】
    AUDIOBOOKSHELF_API_PASSWORD=xxxx  # Audiobookshelf API 密码
    AUDIOBOOKSHELF_COPY_FROM_ID="149c8dsdfs" # 权限模板ID

    # 邀请码和续期码配置 
    INVITE_CODE_SYSTEM_ENABLED=True 
    INVITE_CODE_LENGTH=10 
    INVITE_CODE_EXPIRATION_DAYS=14 # 邀请码有效期
    RENEWAL_CODE_EXPIRATION_DAYS=14 # 续期码有效期
    INVITE_CODE_PRICE=100 # 邀请码的积分价格
    CREATE_USER_EXPIRATION_DAYS=365 # 注册用户默认有效期

    # 状态系统配置
    ENABLE_EXPIRED_USER_CLEAN=False 
    EXPIRED_DAYS=30 # 用户过期题署
    WARNING_DAYS=27 # 用户警告天数
    CLEAN_INTERVAL=2592000 # 清理用户时间

    # Bot消息清理配置
    ENABLE_MESSAGE_CLEANER=False # 是否开启消息清理系统，默认关闭
    DELAY_INTERVAL=5
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
4. [可选] **使用 Docker Compose 运行容器：**
    ```bash
    docker-compose up -d
    ```

## 如何使用

> 为了提升交互体验，命令已经改为为面板，可选命令是否注册为命令，默认无注册命令。/help 会提供更多命令信息

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

## 待办事项

-  [ ] 添加对更多 Web 应用的支持。
-  [ ] 为机器人逻辑添加更多测试。
-  [ ] 添加更多功能，例如群组管理和媒体管理。

## 如何贡献

欢迎贡献！请 fork 仓库并提交 pull request。