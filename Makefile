.PHONY=all migrate test test-in-docker run run-in-docker


migrate:
	uv run alembic upgrade head

test-in-docker:
	docker-compose -f docker-compose-tests.yaml up -d postgres redis 
	docker-compose -f docker-compose-tests.yaml up --build --abort-on-container-exit --exit-code-from app app
	docker-compose -f docker-compose-tests.yaml down

test:
	uv run pytest -v

admin-user:
	uv run alembic upgrade head
	uv run seed_superuser.py

run:
	docker-compose up -d postgres redis 
	./seed/entrypoint.sh
	uv run ./run.py && docker-compose down

run-in-docker:
	docker-compose up -d postgres redis 
	docker-compose up --build --abort-on-container-exit --exit-code-from app app 
	
	docker-compose down
dev:
	docker-compose up -d postgres redis 
	./seed/entrypoint.sh
	uv run ./run.py