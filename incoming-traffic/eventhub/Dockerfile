FROM redis:6

ARG uid=1000

RUN useradd -d /home/user -m -s /bin/bash -u $uid user \
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

COPY entrypoint.sh /usr/local/bin/entrypoint.sh

WORKDIR /home/user

USER $uid

ENTRYPOINT ["/bin/sh", "/usr/local/bin/entrypoint.sh"]
