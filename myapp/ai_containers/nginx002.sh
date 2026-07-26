#!/bin/sh
docker run -d --name=nginx --hostname=nginx002 -p 2280:80 -p 22443:443 nginx:002

