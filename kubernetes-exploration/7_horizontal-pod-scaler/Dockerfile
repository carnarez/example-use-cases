FROM python:slim

WORKDIR /usr/src

RUN pip --no-cache-dir install falcon gunicorn matplotlib numpy

COPY heavy.py .

USER 405

ENTRYPOINT gunicorn --bind 0.0.0.0:5000 --log-level=WARNING --timeout 900 heavy:api
