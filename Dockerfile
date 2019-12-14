FROM python:3.8-alpine AS geeksbot-web

ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONUNBUFFERED 1

RUN adduser --disabled-password --home=/home/geeksbot --gecos "" geeksbot
RUN echo "geeksbot ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
RUN echo "geeksbot:docker" | chpasswd

RUN apk update && \
        apk add --virtual build-deps gcc python3-dev musl-dev postgresql-dev \
        # Pillow dependencies
        && apk add jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev \
        # CFFI dependencies
        && apk add libffi-dev py-cffi \
        # Translations dependencies
        && apk add gettext \
        # https://docs.djangoproject.com/en/dev/ref/django-admin/#dbshell
        && apk add postgresql-client

RUN mkdir /code

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

RUN pip install --upgrade pip
RUN pip install virtualenv

WORKDIR /code

RUN apk update && apk add nginx && apk add supervisor

COPY requirements/base.txt .
COPY requirements/production.txt .
COPY requirements/web.txt .

RUN pip install -r production.txt
RUN pip install -r web.txt

RUN rm -f /etc/nginx/sites-enabled/default
RUN rm -f /etc/nginx/conf.d/default.conf
COPY ./services/nginx.conf /etc/nginx/nginx.conf
COPY ./services/geeksbot.conf /etc/nginx/sites-enabled/geeksbot
COPY ./services/gunicorn.conf /etc/gunicorn.conf
COPY ./services/supervisord.conf /etc/supervisor/supervisord.conf
COPY ./services/supervisor_geeksbot.conf /etc/supervisor/conf.d/geeksbot.conf
COPY ./ssl_certs/geeksbot_app/geeksbot_app_cert_chain.crt /etc/ssl/geeksbot_app_cert_chain.crt
COPY ./ssl_certs/geeksbot_app/geeksbot.app.key /etc/ssl/geeksbot.app.key
COPY ./.env /code/

RUN rm -rf /tmp/*

RUN mkdir -p /tmp/logs/nginx
RUN mkdir -p /tmp/logs/geeksbot
RUN mkdir -p /code/geeksbot_web
COPY ./* /code/

WORKDIR /code/geeksbot_web

# RUN sed -i 's/\r$//g' ./entrypoint
# RUN chmod +x ./entrypoint

EXPOSE 80 8000 443

ENTRYPOINT [ "./entrypoint" ]