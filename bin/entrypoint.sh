#!/bin/bash

if [ "$ENV" = "development" ]; then
  echo "Running Development Server"
  alembic upgrade head
  exec "uvicorn" "app:app" "--reload" "--host" "0.0.0.0" "--port" "8000"
elif [ "$ENV" = "production" ]; then
  echo "Running Production Server"
  alembic upgrade head
  exec "gunicorn" "-w" "4" "-b" "0.0.0.0:8000" "app:app" "-k" "uvicorn.workers.UvicornWorker"
fi
