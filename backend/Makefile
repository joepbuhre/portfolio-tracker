dev:
	flask --app app --debug run
preview:
	waitress-serve --listen=*:5000 app:app
build:
	docker build ../ -t portfolio-tracker
reqs:
	pipreqs --ignore  .\.venv --force .\

serve:
	docker run --rm -it --env-file .env -p 5000:5000 portfolio-tracker 