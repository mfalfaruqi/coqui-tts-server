# Coqui TTS Server

A small Dockerized Coqui TTS HTTP server that serves simple OpenAI compatible API:

- [`POST /v1/audio/speech`](server.py:168) &rarr; returns `audio/mpeg`

## Run with Docker

```bash
cp .env.example .env
docker-compose up --build
```

Server will usually be at:

- `http://localhost:8000/v1/audio/speech`

## Run locally (no Docker)

```bash
pip install -r requirements.txt
python server.py
```

## Configure models

Edit [`tts_models.json`](tts_models.json) to list the models you want to preload:

```json
[
  {
    "model_name": "tts_models/multilingual/multi-dataset/xtts_v2",
    "default_voice": "Craig Gutsy"
  },
  {
    "model_name": "tts_models/ara/fairseq/vits",
    "default_voice": "speakers/default.wav"
  }
]
```

- `model_name` – Coqui TTS model id
- `default_voice` – optional; speaker name or path to a WAV file

Each model in this file is loaded once at startup. The `model` field in the request must match one of these `model_name` values.

## Call the API

Basic example:

```bash
curl -X POST "http://localhost:8000/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts_models/multilingual/multi-dataset/xtts_v2",
    "input": "Hello from Coqui TTS"
  }' \
  --output output.mp3
```

Optional JSON fields:

- `voice` – overrides the default voice for this request
- `instructions` – language code (for multilingual models), default `"en"`
