#!/bin/bash

yum update -y
export AWS_DEFAULT_REGION='us-east-1'
instance_id=$(wget -q -O - http://169.254.169.254/latest/meta-data/instance-id)
aws ec2 associate-address --instance-id $instance_id --public-ip "34.238.62.161"
mkdir /code || exit
cd /code || exit
git clone git@github.com:dustinpianalto/geeksbot_web.git
cd geeksbot_web || exit
docker build . -t geeksbot_web || exit
docker run -d -v /code/geeksbot_web:/code -v /root/.ssh:/root/.ssh:ro --name geeksbot_web --restart always geeksbot_web:latest || exit
