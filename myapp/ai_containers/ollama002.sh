#!/bin/sh
docker run -d --name ollama --hostname ollama002 -v /data/ollama/training:/root/.ollama -p 11434:11434 ollama/ollama

