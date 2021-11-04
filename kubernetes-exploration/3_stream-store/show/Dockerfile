FROM python:alpine

RUN apk --no-cache add thttpd \
 && rm -rf /var/cache/apk/*

COPY entrypoint.sh /usr/src

WORKDIR /var/www/http

COPY style.css .
COPY index.html .
