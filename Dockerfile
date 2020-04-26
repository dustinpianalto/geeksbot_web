FROM python:3.8-alpine AS geeksbot-web

ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONUNBUFFERED 1

RUN adduser --disabled-password --home /home/geeksbot --gecos "" geeksbot
RUN echo "geeksbot ALL (ALL) NOPASSWD: ALL" >> /etc/sudoers
RUN echo "geeksbot:docker" | chpasswd

RUN apk update && \
        apk add gcc python3-dev musl-dev postgresql-dev \
        # Pillow dependencies
        && apk add jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev \
        # CFFI dependencies
        && apk add libffi-dev py-cffi \
        # Translations dependencies
        && apk add gettext \
        # https://docs.djangoproject.com/en/dev/ref/django-admin/#dbshell
        && apk add postgresql-client make git

RUN mkdir /code

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

RUN pip install --upgrade pip
RUN pip install virtualenv

WORKDIR /code

RUN apk update && apk add nginx && apk add supervisor

RUN mkdir requirements

COPY requirements/base.txt requirements/base.txt
COPY requirements/production.txt requirements/production.txt
RUN pip install -r requirements/production.txt

COPY requirements/web.txt requirements/web.txt
RUN pip install -r requirements/web.txt

RUN rm -f /etc/nginx/sites-enabled/default
RUN rm -f /etc/nginx/conf.d/default.conf
COPY ./services/nginx.conf /etc/nginx/nginx.conf
COPY ./services/geeksbot.conf /etc/nginx/sites-enabled/geeksbot
COPY ./services/gunicorn.conf /etc/gunicorn.conf
COPY ./services/supervisord.conf /etc/supervisor/supervisord.conf
COPY ./services/supervisor_geeksbot.conf /etc/supervisor/conf.d/geeksbot.conf

RUN rm -rf /tmp/*

RUN mkdir -p /tmp/logs/nginx
RUN mkdir -p /tmp/logs/geeksbot
RUN mkdir -p /code/geeksbot_web

# PostgreSQL DB Connection Info
ENV POSTGRES_HOST geeksbot-db.c3omjx35ryzn.us-east-1.rds.amazonaws.com
ENV POSTGRES_DB geeksbot
ENV POSTGRES_PORT 5432
ENV POSTGRES_USER postgres
ENV CONN_MAX_AGE 0
# Redis Connection Info
ENV REDIS_DB 0
ENV REDIS_ENABLED true
ENV REDIS_HOST redis.geeksbot.com
ENV REDIS_PORT 6379


ENV USE_DOCKER yes
# Django
ENV DJANGO_SETTINGS_MODULE config.settings.production
ENV DJANGO_ALLOWED_HOSTS .geeksbot.app,localhost
ENV DJANGO_SECURE_SSL_REDIRECT False
ENV DJANGO_ACCOUNT_ALLOW_REGISTRATION True
# Email
ENV DJANGO_SERVER_EMAIL geeksbot@geeksbot.app
ENV MAILGUN_DOMAIN mail.geeksbot.app
# Gunicorn
ENV WEB_CONCURRENCY 4

EXPOSE 80 8000 443

COPY entrypoint .

ENTRYPOINT [ "./entrypoint" ]
