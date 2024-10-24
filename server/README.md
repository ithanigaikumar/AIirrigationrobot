# Server setup

## Prerequisites

Before you start, ensure you have the `docker`, and complete `.env` file with appropriate secrets.

## Steps

To set up the project, follow these steps:

1. **Build and run FastAPI server:**
    ```bash
    docker build -t server . 
    docker run -p 8000:80000 server

2. **Start other backend services:**
    ```bash
    docker compose up -d
