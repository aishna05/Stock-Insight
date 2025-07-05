run-predict:
	docker-compose run --rm predictor python manage.py predict --ticker AAPL

run-predict-all:
	docker-compose run --rm predictor python manage.py predict_all

run-bot:
	docker-compose run --rm telegram_bot
