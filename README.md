# Stock-Insight


A full-stack Django-based stock prediction platform using LSTM models, Tailwind CSS for UI, and Telegram bot integration. Easily deployable via Docker.

---

## 🚀 Features

- 📊 Predict next-day stock prices using LSTM
- 🖼 Visualize predictions vs actual prices with matplotlib
- 💬 Telegram Bot integration to request predictions
- 🌐 Beautiful Tailwind CSS frontend
- 🐳 Dockerized for ease of deployment

---

## 🧾 Requirements

- Docker & Docker Compose
- Telegram account (for bot)
- Python 3.10 (if running locally without Docker)

---

## 🛠 Project Setup

### 1. Clone the Repo

```bash
git clone https://github.com/aishna05/Stock-Insight.git
cd Stock-Insight

```
### 2. ADD .env file 


Create a .env file from the provided example.env.

cp example.env .env

then update their own vales

### 3. Docker SETUP

build container and run web server

```bash 
docker-compose build
docker-compose up web
```

Run the bot 
```bash
docker-compose run --rm telegram_bot
```

 Get Telegram Bot Link
Search for BotFather on Telegram

Send /newbot

Follow prompts to name your bot and get a token
Add that token in .env under TELEGRAM_BOT_TOKEN
Get your bot link: https://t.me/<your_bot_username>

### 4. Predict Stock via CLI

Run Prediction Script
```bash
docker-compose run --rm predictor
```
This will run the default ticker (like TSLA if coded).

Run for a Specific Ticker
```bash

docker-compose run --rm predictor python manage.py predict --ticker AAPL

```

