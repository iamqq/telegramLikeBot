# Private Registry Guide

This guide explains how to build, push, and run the Telegram Like Bot using your private registry at `192.168.86.238:5000`.

## Prerequisites

- Docker installed on your machine.
- Access to the private registry at `192.168.86.238:5000`.
- If the registry is not using HTTPS, you may need to configure Docker to allow insecure registries.
  - Edit `/etc/docker/daemon.json` (Linux) or Docker Desktop settings:
    ```json
    {
      "insecure-registries" : ["192.168.86.238:5000"]
    }
    ```
  - Restart Docker daemon:
    ```bash
    sudo systemctl restart docker
    ```

## Build and Push

1.  **Build the image**:
    ```bash
    docker build -t 192.168.86.238:5000/telegram-like-bot .
    ```

2.  **Push to registry**:
    ```bash
    docker push 192.168.86.238:5000/telegram-like-bot
    ```

## Deployment (via Portainer or Docker Compose)

### Using Docker Compose

1.  Ensure you have the `docker-compose.yml` file on your server.
2.  Set your API Token:
    ```bash
    export API_TOKEN=your_telegram_bot_token
    ```
3.  Run the bot:
    ```bash
    docker-compose up -d
    ```

### Using Portainer

1.  **Add Registry**:
    - Go to Registries -> Add Registry.
    - select "Custom registry".
    - Name: `My Registry` (or anything you like).
    - Registry URL: `192.168.86.238:5000`.
    - (Optional) Authentication if you configured it.

2.  **Deploy Stack / Container**:
    - Create a new Stack or Container.
    - Image: `192.168.86.238:5000/telegram-like-bot`
    - **Env Vars**: Add `API_TOKEN` with your bot token.
    - **Volumes**: Map a host path to `/app/data` to persist the database.
       - e.g., Host: `/path/to/bot/data` -> Container: `/app/data`
    - **Env Vars (Database)**: Add `DATABASE_URL=/app/data/bot.db`.
