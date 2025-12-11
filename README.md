# Coqui Server

A minimal Python-based server packaged with Docker for quick deployment.

This repository includes:

- server.py
- requirements.txt
- Dockerfile
- docker-compose.yml
- .env.example
- speakers/ (sample audio assets)

Getting started

Prerequisites:

- Docker and Docker Compose (or Python 3.8+ if running locally)

Quick start (Docker)

- Copy the example environment:
  cp .env.example .env

- Build and start the services:
  docker-compose up --build

- The server should be reachable at <http://localhost:8000/> (adjust in docker-compose.yml)

Local development (without Docker)

- Install dependencies:
  pip install -r requirements.txt

- Run the server:
  python server.py

Environment variables

See .env.example for a template of the required variables.

License

This repository does not include a license file. Use at your own risk.
