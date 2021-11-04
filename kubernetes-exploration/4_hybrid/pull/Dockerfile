FROM python:alpine

WORKDIR /usr/src

COPY requirements.txt .
RUN apk --no-cache --virtual .build-deps add build-base gcc musl-dev postgresql-dev \
 && apk --no-cache add postgresql \
 && pip install --no-cache-dir -r requirements.txt \
 && apk del .build-deps \
 && rm requirements.txt

COPY p*.py ./
COPY supervisord.conf /etc

USER 405
