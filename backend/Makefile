dev:
	uvicorn app:app --reload
preview:
	waitress-serve --listen=*:5000 app:app
build:
	docker build ../ -t portfolio-tracker
reqs:
	pipreqs --ignore  ".\.venv" --force .\

setupdev:
	pip install -r requirements.txt && pip install pipreqs
serve:
	docker run --rm -it --env-file .env -p 5000:5000 portfolio-tracker 