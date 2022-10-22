FROM python:3.10-slim

ENV PYTHONUNBUFFERED 1

ENV PYTHONDONTWRITEBYTECODE 1

RUN mkdir /etc/api

WORKDIR /etc/api

COPY requirements/prod.txt .

RUN pip install --no-cache-dir --upgrade -r prod.txt

COPY src .

WORKDIR /etc/api/src

CMD [ "gunicorn", "asgi:app", "--workers 4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind 0.0.0.0:80" ]

# gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:80
