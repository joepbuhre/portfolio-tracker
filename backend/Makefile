dev:
	uvicorn app:app --reload
preview:
	waitress-serve --listen=*:5000 app:app
build:
	docker build ../ -t portfolio-tracker
serve:
	docker run --rm -it --env-file .env -p 5000:5000 portfolio-tracker 
dramatiq:
	dramatiq tasks
upgrade:
	alembic upgrade head
migration:
	@echo alembic revision --autogenerate -m "<your message here>"
