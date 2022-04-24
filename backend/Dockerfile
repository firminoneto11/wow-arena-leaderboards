FROM python:3.10

WORKDIR /api

COPY requirements.txt .

RUN pip install -r requirements.txt .

COPY src .

WORKDIR /api/src

CMD [ "uvicorn", "main:api" ]
