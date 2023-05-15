serve:
	waitress-serve --listen=*:5000 app:app
build:
	docker build ../ -t portfolio-tracker
dev:
	flask --app app --debug run
reqs:
	pipreqs --ignore  .\.venv --force .\