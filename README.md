# Coqui TTS Server

A small Dockerized Coqui TTS HTTP server that serves simple OpenAI compatible API:

- [`POST /v1/audio/speech`](server.py:168) &rarr; returns default `audio/mpeg`

## Run with Docker

```bash
cp .env.example .env
docker-compose up -d
```

Server will be at port 8000 (configurable in env PORT):

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
- `default_voice` – speaker name from preset data or path to a WAV file

Each model in this file is loaded once at startup. The `model` field in the request must match one of these `model_name` values. Preset default voices must match the speaker name from preset model's speaker data. See [here](https://github.com/idiap/coqui-ai-TTS/?tab=readme-ov-file#multi-speaker-models) for getting speaker list.

## Call the API

Basic example:

```bash
curl -X POST "http://localhost:8000/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts_models/multilingual/multi-dataset/xtts_v2",
    "input": "Hello from Coqui TTS",
    "voice": "Craig Gutsy",
    "response_format": "mp3"
  }'
```

JSON fields:

- `model` – model name from preset data
- `input` – text to be converted to speech
- `voice` – (optional) overrides the default speaker voice for this request. make sure the speaker name is available in the preset data or the path to a WAV file
- `response_format` – (optional) response format, default `mp3`, available formats: WAV, MP3, OGG, FLV, MP4, AAC, and WMA
