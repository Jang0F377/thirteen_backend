#!/bin/bash

if [ "$ENV" = "development" ]; then
  echo "Running Development Server"
  alembic upgrade head
  exec "fastapi" "dev" "app.py" "--host" "0.0.0.0" "--port" "8000"
elif [ "$ENV" = "production" ]; then
  echo "Running Production Server"
  alembic upgrade head
  exec "fastapi" "run" "app.py" "--port" "8000"
fi
