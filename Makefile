up:
	docker compose up

down:
	docker compose down
	docker ps -a

build:
	docker compose up -d
	echo "Waiting for containers to finish booting..."
	sleep 10
	docker compose exec web ./venv/bin/python3 manage.py makemigrations users
	docker compose exec web ./venv/bin/python3 manage.py migrate --noinput
	#docker compose exec web ./venv/bin/python3 manage.py collectstatic
	echo "Create super user"
	docker compose exec web ./venv/bin/python3 manage.py createsuperuser

migrate:
	@if [ ${module} ]; then \
      	docker compose exec web ./venv/bin/python3 manage.py migrate ${module}; \
    else \
      	docker compose exec web ./venv/bin/python3 manage.py migrate; \
    fi

migrations:
	@if [ ${module} ]; then \
      	docker compose exec web ./venv/bin/python3 manage.py makemigrations ${module}; \
    else \
      	docker compose exec web ./venv/bin/python3 manage.py makemigrations; \
    fi

bash:
	docker compose exec web /bin/bash

startapp:
	docker compose exec web ./venv/bin/python3 manage.py startapp ${appname}

requirements:
	docker compose exec web ./venv/bin/python3 -m pip install -r requirements.txt #install web container
	docker compose exec beat ./venv/bin/python3 -m pip install -r requirements.txt #install celery beat container
	python3 -m pip install -r requirements.txt #install locally

