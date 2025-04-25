.PHONY: install dev start format lint clean

install:
	poetry install

dev:
	poetry run uvicorn main:app --host 0.0.0.0 --port 6543 --reload

start:
	poetry run uvicorn main:app --host 0.0.0.0 --port 6543

format:
	poetry run black .
	poetry run isort .

lint:
	poetry run flake8 .

clean:
	rm -rf __pycache__
	rm -rf */__pycache__
	rm -rf */*/__pycache__
	rm -rf dist
	rm -rf build
