FROM python:3.10

RUN mkdir /api

WORKDIR /api

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt .

COPY src .

WORKDIR /api/src

# CMD [ "uvicorn", "main:api" ]

# Cria um process manager a partir do Gunicorn e ele spawna 4 workers onde cada Worker é um Uvicorn contendo um processo isolado da API
CMD [ "gunicorn", "main:app", "--workers 4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind 0.0.0.0:80" ]
