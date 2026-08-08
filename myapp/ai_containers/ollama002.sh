#!/bin/sh
docker run -d --name ollama --hostname ollama002 --link ollamarepo:airepository.saicmotor.com -v /data/ollama/training:/root/.ollama -p 11434:11434 ollama/ollama

