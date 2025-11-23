# Telegram Like Bot

A Telegram bot that automatically adds reaction buttons (likes) to photos and videos sent in a chat. It supports albums, custom buttons, and tracks votes directly in the message text.

## Features

*   **Automatic Reactions**: Adds buttons to every new photo or video.
*   **Album Support**: Intelligently groups media albums and sends a single set of buttons for the whole group.
*   **Stateless Votes**: Stores likes directly in the message text, making it fast and allowing multiple reactions per user.
*   **Customizable**:
    *   Set custom buttons for the whole chat: `/chatlikes 👍 👎`
    *   Set custom buttons for yourself: `/userlikes 🔥 💩`
*   **Async Architecture**: Built with `aiogram` and `aiosqlite` for high performance.

## Setup

1.  **Clone the repository**
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Environment Variables**:
    Create a `.env` file or set these variables:
    *   `API_TOKEN`: Your Telegram Bot Token (from @BotFather).
    *   `DATABASE_URL`: Path to sqlite file (default: `bot.db`).

4.  **Run the bot**:
    ```bash
    python server.py
    ```

## Commands

*   `/start` - Show welcome message and help.
*   `/chatlikes [emojis]` - Set default buttons for this chat.
    *   Example: `/chatlikes 👍 👎`
*   `/userlikes [emojis]` - Set your personal buttons for this chat.
    *   Example: `/userlikes ❤️ 🔥`
*   `/currentlikes` - Show current settings.

## Limitations

*   **Message Length**: Since votes are stored in the text, there is a limit of 4096 characters (approx. 100-200 users).
*   **User Names**: Votes are tied to the user's display name. If a user changes their name, their previous votes may not be recognized correctly until they vote again.
