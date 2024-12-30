# 🚀 This project is guided by the excellent Gemini AI assistant! 🤖

# User Management System for Navidrome and Emby with Telegram Bot

## Project Description

This system is a powerful and flexible user management system designed to manage users of Navidrome and Emby media servers. It is controlled by a Telegram bot, allowing you to manage users, generate invite codes, manage user scores, and more. This project is built using Python with the help of pyTelegramBotAPI, sqlite, and loguru.

## Project Features

-   **User Management:** Create, read, update, and delete users on Navidrome and Emby.
-   **Invite Code System:** Generate, validate, and use invite codes.
-   **User Score Management:** Manage user scores, including adding, reducing, setting, and check-in for scores.
-   **Telegram Bot Control:** Use Telegram bot to manage the whole system.
-   **Admin and User Modes:** Different Telegram users have different levels of permissions. Administrators can manage all users, and general users can manage their own information.
-   **Database Support:** Use SQLite database to store user data, invite codes, and user scores.
-   **Log System:** Use `loguru` to record system activities.

## How to Install

You can choose to install this system either by traditional method or using Docker and Docker Compose.

**Traditional Method**

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/SenLief/RegManagerBot.git
    cd RegManagerBot
    ```
2.  **(Optional) Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate # On Linux/macOS
    venv\Scripts\activate # On Windows
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure `.env` file:** Create a `.env` file in the project root directory, and add the following configurations. Please replace the placeholder with your actual data.
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
5.  **(Optional) Create a `regmangerbot.service` file, replace the placeholder with your actual data:**
    ```
    [Unit]
    Description=RegManagerBot Telegram Bot
    After=network.target

    [Service]
    User=your_username  # Replace with your username
    Group=your_username # Replace with your username
    WorkingDirectory=/path/to/your/project  # Replace with your project path
    ExecStart=/path/to/your/virtualenv/bin/python /path/to/your/project/main.py # Replace with your virtualenv path and project path
    Restart=on-failure
    RestartSec=10

    [Install]
    WantedBy=multi-user.target
    ```
6.  **(Optional) Start the service:**
    ```bash
    sudo cp regmangerbot.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable regmangerbot.service
    sudo systemctl start regmangerbot.service
    ```

**Docker and Docker Compose Method**

1. **Clone the repository:**
    ```bash
    git clone https://github.com/SenLief/RegManagerBot.git
    cd RegManagerBot
    ```
2. **Configure the `.env` file:** Create a `.env` file in the project root directory, and add the required configurations same as the traditional method
3.  **Run the application with Docker Compose:**
    ```bash
    docker run -d --name regmanagerbot \
    -v /path/to/your/project/data:/app/data \
    --env-file /path/to/your/project/.env \
     janzbff/regmanagerbot:latest
    ```
   **Replace `/path/to/your/project` with your project path**

## How to Use

1.  **Run the application:**
    - For the **traditional method**, run `python main.py`.
    - For the **Docker and Docker Compose method**, the application will run automatically in background
2.  **Start a conversation with the Telegram bot:** Use your configured Telegram bot to send commands to manage the system.
3.  **Available commands for administrators:**
    -   `/generate_code`: Generate a new invite code.
    -   `/invite`: View all invite codes.
    -   `/toggle_invite_code_system`: Enable/Disable the invite code system.
    -   `/set_score <telegram_id> <score>`: Set user's score.
    -   `/get_score <telegram_id>` or `/score <telegram_id>`: View user's score.
    -   `/add_score <telegram_id> <score>`: Add score to a user.
    -   `/reduce_score <telegram_id> <score>`: Reduce score from a user.
    -   `/set_price <config_name> <price>`: set config with price, e.g. `/set_price INVITE_CODE_PRICE 150`
    -   `/userinfo <telegram_id>`: Get user information by telegram id.
    -   `/userinfo_by_username <username>`: Get user information by username.
    -   `/stats`: Get register user statistics.
4.  **Available commands for general users:**
    -   `/start`: Get user information and all command
    -   `/register <username> <password>`: Register user (with username and password).
    -   `/register <username> <password> <invite_code>`: Register user with invite code (with username, password and invite code).
    -   `/info`: View user information.
    -   `/deleteuser`: Delete user account.
    -  `/score`: View your score.
    -  `/checkin`: Check-in to earn score.
    -   `/buyinvite`: Buy invite code.
    -   `/reset_password`: Reset user password.
    -   `/give`: Give score to another user.
    -   `/bind`: Bind user account.
    -  `/unbind`: Unbind user account.

## How to Contribute

We welcome all contributions to this project. If you want to help improve the system, please:

1.  **Fork the repository.**
2.  **Create a new branch for your feature or fix.**
3.  **Commit your changes.**
4.  **Push to your branch.**
5.  **Create a pull request.**

## TODO

-   Add support for more web applications.
-   Add more tests for bot logic.
-   Add more features, such as group management and media management.
-   Add more powerful and flexible user permission system.
-   Add UI for the system.

## For Chinese readers, please refer to [README-zh.md](README-zh.md).