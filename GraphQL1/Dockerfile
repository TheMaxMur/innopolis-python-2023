FROM python:3.11.3-slim-buster

COPY requirements.txt /tmp/requirements.txt

RUN apt update && \
    apt install libmariadb-dev g++ libpq-dev gcc -y 

RUN python3 -m pip install -r /tmp/requirements.txt

RUN groupadd python && \
    useradd python -g python 

COPY . /app

RUN chown -R python:python /app

WORKDIR /app

USER python 

CMD ["flask", "run", "--host=0.0.0.0"]
