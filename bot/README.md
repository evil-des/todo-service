### Installation and Running (Manual)
1. Create a new .env file and change all settings:

    `cp .env.example .env`

2. Install all dependencies:

    `poetry install`
3. Set sqlalchemy.uri in alembic.ini, then run migration:

    `poetry run python -m alembic upgrade head`

4. Run Telegram bot:

    `python3 app/bot.py`


### Auto install by Docker
1. Create a new .env file:

    `cp .env.example .env.docker`

2. Change desired options in docker-compose.yml (do not forget to update sqlalchemy.uri in alembic.ini)

3. Run this command for the first time build:

    `docker-compose up -d --build`