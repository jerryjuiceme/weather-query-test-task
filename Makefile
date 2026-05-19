.PHONY=all init migrate test test-in-docker run run-in-docker up-docker seed-admin-user

ifneq (,$(wildcard .env))
  include .env
  export
endif

init:
	chmod +x ./seed/init.sh && ./seed/init.sh

run:
	docker-compose up -d postgres redis 
	./seed/entrypoint_local.sh
	uv run ./run.py && docker-compose down

run-in-docker:
	docker-compose up -d postgres redis 
	docker-compose up --build --abort-on-container-exit --exit-code-from app app 
	
	docker-compose down


test-in-docker:
	docker-compose -f docker-compose-tests.yaml up -d postgres redis 
	docker-compose -f docker-compose-tests.yaml up --build --abort-on-container-exit --exit-code-from app app
	docker-compose -f docker-compose-tests.yaml down

test:
	uv run pytest -v


up-docker:
	docker-compose up -d postgres redis 

down-docker:
	docker-compose down -v
	
migrate:
	uv run alembic upgrade head

seed-admin-user:
	uv run alembic upgrade head
	uv run seed_superuser.py


