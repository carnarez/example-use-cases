FROM python:slim

ARG uid=1000

ENV PYTHONUNBUFFERED=1

COPY requirements.txt /tmp/requirements.txt

RUN useradd -M -s /bin/bash -u $uid user \
 && pip install --no-cache-dir -r /tmp/requirements.txt \
 && echo "Europe/Amsterdam" > /etc/timezone \
 && rm /etc/localtime \
 && dpkg-reconfigure -f noninteractive tzdata \
 && apt-get autoremove --allow-remove-essential -y \
 && apt-get clean -y \
 && rm -fr /tmp/* \
           /var/cache/debconf/*-old \
           /var/lib/apt \
           /var/lib/cache \
           /var/lib/dpkg \
           /var/lib/log

WORKDIR /usr/src

COPY images images
COPY push.py push.py

USER $uid

ENTRYPOINT ["/usr/local/bin/python", "/usr/src/push.py"]
