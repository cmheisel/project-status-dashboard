FROM debian:jessie

RUN apt-get update -y && apt-get install -y \
    python3 \
    python3-dev \
    python3-venv \
    python3-pip \
    libpq-dev \
    supervisor \
    python-pip \
    git \
    && pip install supervisor==3.2.1 supervisor-stdout==0.1.1 \
    && pip3 install -U pip \
    && rm -rf /var/lib/apt/lists/*

RUN pyvenv-3.4 /app-ve && mkdir -p /app/
COPY ./container /

WORKDIR /app/
COPY ./requirements*.txt /app/
RUN /app-ve/bin/pip install -r requirements.txt
COPY ./ /app

EXPOSE 8000
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
