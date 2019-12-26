#!/bin/bash

docker build . -t geeksbot_web || exit
docker run -d -v /code/geeksbot_web:/code -v /root/.ssh:/root/.ssh:ro -v /root/ssl_certs:/etc/ssl:ro -p 80:80 -p 443:443 -p 8000:8000 --name geeksbot_web --restart always geeksbot_web:latest || exit
