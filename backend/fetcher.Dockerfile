FROM python:3.10

RUN mkdir /fetcher

WORKDIR /fetcher

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt .

COPY src .

WORKDIR /fetcher/src

CMD [ "python", "fetcher_service.py" ]
