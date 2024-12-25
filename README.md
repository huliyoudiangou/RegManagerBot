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

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/SenLief/RegManagerBot.git
    cd RegManagerBot
    ```
2.  **Create a virtual environment (optional):**
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
    DATABASE_URL=".data/data.db"
    TELEGRAM_BOT_TOKEN=your_telegram_bot_token
    ADMIN_TELEGRAM_IDS=123456789,987654321
    NAVIDROME_API_URL=http://your_navidrome_url/api
    NAVIDROME_API_USERNAME=your_navidrome_username
    NAVIDROME_API_PASSWORD=your_navidrome_password
    EMBY_API_URL=http://your_emby_url/emby
    EMBY_API_KEY=your_emby_api_key
    INVITE_CODE_LENGTH=10
    INVITE_CODE_EXPIRATION_DAYS=14
    INVITE_CODE_SYSTEM_ENABLED=False
    INVITE_CODE_PRICE=100
    ```

## How to Use

1.  **Run the application:**
    ```bash
    python main.py
    ```
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
4. **Available commands for general users:**
    -   `/register <username> <password>`: Register user
    -   `/register <username> <password> <invite_code>`: Register user with invite code
    -   `/start`: Get user information and all command
    -   `/info`: Get user information
    -   `/use_code <username> <password> <invite_code>`: Use invite code
    -  `/deleteuser`: Delete user
    -   `/score`: View your score
    -   `/checkin`: Check-in to earn score
    -   `/buyinvite`: Buy invite code

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