FROM python:3.8-buster

ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get upgrade -y && apt-get autoremove -y && apt-get install -y wget
ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

RUN mkdir -p /usr/src/
WORKDIR /usr/src/

RUN cd /usr/src/
COPY src/requirements.txt src/requirements-dev.txt ./
RUN python -m pip install --upgrade pip setuptools
RUN pip install -r requirements.txt -r requirements-dev.txt

COPY src/ .
RUN make dev

ENV FLASK_APP='web_app.web_app.app:create_app'
ENTRYPOINT ["dockerize", "-wait", "tcp://database:5432"]

