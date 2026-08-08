#!/bin/sh
docker run -d --name=nginx --hostname=nginx003 -p 2280:80 -p 22443:443 nginx:003

