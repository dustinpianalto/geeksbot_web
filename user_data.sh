#!/bin/bash

docker build . -t geeksbot_web || exit
docker run -d -v /code/geeksbot_web:/code -v /root/.ssh:/root/.ssh:ro -v /root/ssl_certs:/etc/ssl:ro --name geeksbot_web --restart always geeksbot_web:latest || exit
