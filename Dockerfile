FROM python:3.8-buster

ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y wget
ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

WORKDIR /usr/src/app
COPY src/requirements.txt src/requirements-dev.txt ./
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt -r requirements-dev.txt

COPY src/ ./
RUN make dev

ENV FLASK_APP='web_app.app:create_app'
CMD ["flask", "run", "--host=0.0.0.0", "--reload"]
ENTRYPOINT ["dockerize", "-wait", "tcp://database:5432"]

