# 🚀 This project is guided by the excellent Gemini AI assistant and Deepseek V3! 🤖

# A Telegram Bot-based User Management System for Navidrome, Emby, Audiobookshelf, and Other Services Without Web Registration.

[English](README.md) | [中文](README-zh.md)

## Project Description

This project primarily provides a Telegram Bot-based user management system for self-hosted services such as Navidrome, Emby, Audiobookshelf, etc. It offers functionalities like registration, deletion, banning, activation, and implements local Bot features such as points and invitation code/renewal code systems.

## Project Features

-   **Multi-Service Support:** Supports self-hosted services like Navidrome, Emby, Audiobookshelf, etc. The interface is abstracted, allowing easy integration with other services.
-   **User Management:** Provides registration, deletion, banning, username/password reset, and more for self-hosted services.
-   **Registration Template:** Offers a registration template for users, ensuring that registered users have the same permissions as the template.
-   **Invitation Code System:** Generates, verifies, and uses invitation codes and renewal codes.
-   **User Points Management:** Manages user points, including adding, reducing, setting, and earning points through check-ins.
-   **Admin and User Modes:** Different Telegram users have different permissions. Admins can manage all users, while regular users can manage their own information.
-   **Status Management:** User statuses include normal, banned, expired, etc., with the ability to enable and manage invitation registration systems.
-   **Entertainment System:** Earn points, send random point red packets, etc.

## How It Works

The system interacts with backend services via APIs using service IDs. Except for user management, all other functionalities are implemented locally within the Bot, ensuring no additional load on the backend services.

## Feature Overview

### User Management

-   **Register User:** Users can register with the backend service and set a username and password.
-   **Delete User:** Users can delete their own accounts, and admins can delete any user (currently using a ban mode).
-   **Ban User:** Admins can ban users, preventing them from using the service (optional whether to ban the backend service).
-   **Reset Username and Password:** Users can reset their own usernames and passwords.
-   **User Status Management:** Users can view their status, and admins can manage user statuses.

### Invitation Code System

-   **Generate Invitation Code:** Admins can generate invitation/renewal codes, and regular users can purchase them.
-   **Verify Invitation Code:** The system verifies the validity of invitation/renewal codes.
-   **Use Invitation Code:** Users can register using invitation codes or renew their accounts with renewal codes.

### User Points Management

-   **Add Points:** Admins can add points to users.
-   **Reduce Points:** Admins can reduce points from users.
-   **Set Points:** Admins can set points for users.
-   **Gift Points:** Users can gift points to other registered users.
-   **Check-in to Earn Points:** Users can earn points by checking in.
-   **Points Red Packet:** Users can send points red packets.

### Registration Template

> During the design phase, we considered that different services might have varying permission designs. Default permissions for registered users might not always be user-friendly. Implementing custom permission controls would significantly increase workload. Inspired by Emby's registration model, we decided to allow admins to create a template user with predefined permissions. New users would then inherit these permissions during registration.

1. Create a template user on the service and set the desired permissions.
2. Set the template user's ID in the `.env` file.
3. During registration, the new user will inherit the template user's permissions.

### Logging System

-   **Log System Activities:** Uses `loguru` to log system activities.

## Installation

You can choose to install the system using the traditional method or via Docker and Docker Compose.

**Traditional Method**

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/SenLief/RegManagerBot.git
    cd RegManagerBot
    ```
2.  **(Optional) Create a Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate # On Linux/macOS
    venv\Scripts\activate # On Windows
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure `.env` File:** Create a `.env` file in the project root directory or copy `.env.example`, and add the following configurations. Replace placeholders with actual data.
    ```
    DATABASE_URL="./data/data.db" # Database path
    TELEGRAM_BOT_TOKEN="xxxxxxQzNiZnsqeazgTNg" # Telegram Bot Token
    WEBHOOK_URL="" # http://0.0.0.0:7000 or https://domain.com
    SERVICE_TYPE="emby" # navidrome|emby|audiobookshelf
    ADMIN_TELEGRAM_IDS="xxxx" # Telegram IDs, 23423423,34344234,2342343

    # Navidrome Configuration
    NAVIDROME_API_URL="http://172.18.96.1:4533"
    NAVIDROME_API_USERNAME=xxxx # Requires admin privileges
    NAVIDROME_API_PASSWORD=xxxx

    # Emby Configuration
    EMBY_API_URL="http://172.18.96.1:8096"  # Emby API URL
    EMBY_API_KEY="2b04b0173xxxx929"  # Emby API Key 
    EMBY_API_USERNAME=xxx  # Navidrome API Username 【Prefer API Key】
    EMBY_API_PASSWORD=xxx  # Navidrome API Password
    EMBY_COPY_FROM_ID="xxxxx" # Permission Template ID

    # Audiobookshelf Configuration
    AUDIOBOOKSHELF_API_URL="http://172.18.96.1:13378"
    AUDIOBOOKSHELF_API_KEY=""  # Audiobookshelf API Key
    AUDIOBOOKSHELF_API_USERNAME=xxx  # Audiobookshelf API Username 【Prefer API Key】
    AUDIOBOOKSHELF_API_PASSWORD=xxxx  # Audiobookshelf API Password
    AUDIOBOOKSHELF_COPY_FROM_ID="149c8dsdfs" # Permission Template ID

    # Invitation Code and Renewal Code Configuration 
    INVITE_CODE_SYSTEM_ENABLED=True 
    INVITE_CODE_LENGTH=10 
    INVITE_CODE_EXPIRATION_DAYS=14 # Invitation Code Validity
    RENEWAL_CODE_EXPIRATION_DAYS=14 # Renewal Code Validity
    INVITE_CODE_PRICE=100 # Invitation Code Price in Points
    CREATE_USER_EXPIRATION_DAYS=365 # Default User Validity Period

    # Status System Configuration
    ENABLE_EXPIRED_USER_CLEAN=False 
    EXPIRED_DAYS=30 # User Expiration Period
    WARNING_DAYS=27 # User Warning Period
    CLEAN_INTERVAL=2592000 # User Cleanup Interval

    # Bot Message Cleanup Configuration
    ENABLE_MESSAGE_CLEANER=False # Enable message cleanup system, default off
    DELAY_INTERVAL=5
    ```
5.  **(Optional) Create `regmangerbot.service` File:** Replace placeholders in the file.
    ```
    [Unit]
    Description=RegManagerBot Telegram Bot
    After=network.target

    [Service]
    User=your_username  # Replace with your username
    Group=your_username # Replace with your username
    WorkingDirectory=/path/to/your/project  # Replace with your project path
    ExecStart=/path/to/your/virtualenv/bin/python /path/to/your/project/main.py # Replace with your virtual env path and project path
    Restart=on-failure
    RestartSec=10

    [Install]
    WantedBy=multi-user.target
    ```
6.  **(Optional) Start the Service:**
    ```bash
    sudo cp regmangerbot.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable regmangerbot.service
    sudo systemctl start regmangerbot.service
    ```

**Docker and Docker Compose Method**

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/SenLief/RegManagerBot.git
    cd RegManagerBot
    ```
2.  **Configure `.env` File:** Create a `.env` file in the project root directory, similar to the traditional method.
3.  **Run the Container Using Docker (Replace /path/to/your/project with your project path):**
    ```bash
     docker run -d --name regmanagerbot \
    -v /path/to/your/project/data:/app/data \
    --env-file /path/to/your/project/.env \
     janzbff/regmanagerbot:latest
    ```
4. [Optional] **Run the Container Using Docker Compose:**
    ```bash
    docker-compose up -d
    ```

## Usage

> To enhance interaction, commands have been converted to panels. Commands can optionally be registered as commands; by default, no commands are registered. `/help` provides more command information.

1.  **Run the Application:**
    -   **Traditional Method:** Run `python main.py`.
    -   **Docker and Docker Compose Method:** The application will run automatically in the background.
2.  **Start a Conversation with the Telegram Bot:** Use the configured Telegram Bot to send commands and manage the system.
3.  **Admin Commands:**
    -   `/generate_code`: Generate a new invitation code.
    -   `/invite`: View all invitation codes.
    -   `/toggle_invite_code_system`: Enable/disable the invitation code system.
    -   `/set_score <telegram_id> <score>`: Set user points.
    -   `/get_score <telegram_id>` or `/score <telegram_id>`: View user points.
    -   `/add_score <telegram_id> <score>`: Add points to a user.
    -   `/reduce_score <telegram_id> <score>`: Reduce points from a user.
    -   `/set_price <config_name> <price>`: Set price configurations, e.g., `/set_price INVITE_CODE_PRICE 150`.
    -   `/userinfo <telegram_id>`: Get user info by Telegram ID.
    -   `/userinfo_by_username <username>`: Get user info by username.
    -   `/stats`: Get registered user statistics.
4.  **Regular User Commands:**
   -   `/start`: Get user info and all available commands.
    - `/register <username> <password>`: Register a user (requires username and password).
    - `/register <username> <password> <invite_code>`: Register a user using an invitation code (requires username, password, and invitation code).
    -   `/info`: Get user info.
    -   `/use_code <username> <password> <invite_code>`: Use an invitation code.
    -  `/deleteuser`: Delete a user account.
    -   `/score`: View your points.
    -   `/checkin`: Check-in to earn points.
    -  `/buyinvite`: Purchase an invitation code.
    -  `/reset_password`：Reset password
    -  `/reset_username`：Reset username
    -   `/give`： Give points
    -  `/bind`：Bind service to bot
    - `/unbind`：Unbind 

## To-Do List

-  [ ] Add support for more web applications.
-  [ ] Add more tests for bot logic.
-  [ ] Add more features, such as group management and media management.

## How to Contribute

Contributions are welcome! Please fork the repository and submit a pull request.