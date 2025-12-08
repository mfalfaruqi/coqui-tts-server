# OpenAI-Compatible TTS Server (Coqui XTTSv2 + LitServe)

This project implements an OpenAI-compatible Text-to-Speech (TTS) API using [Coqui XTTSv2](https://github.com/coqui-ai/TTS) and [LitServe](https://github.com/Lightning-AI/litserve). It supports multilingual TTS (including Arabic), voice cloning via reference audio, and speaker selection.

## Features

- **OpenAI Compatibility**: Exposes a `/v1/audio/speech` endpoint compatible with OpenAI's API format.
- **Coqui XTTSv2**: Uses the state-of-the-art XTTSv2 model for high-quality, multilingual speech synthesis.
- **Voice Cloning**: Supports zero-shot voice cloning using `.wav` reference files.
- **Speaker Selection**: Select speakers by filename, index, or pass a speaker name directly to the model.
- **Docker Support**: Easy deployment with Docker and Docker Compose (GPU supported).
- **Configurable**: Environment variables for model selection and default voice.

## Prerequisites

- Python 3.9+ (for local run)
- Docker & Docker Compose (recommended)
- NVIDIA GPU & NVIDIA Container Toolkit (for GPU acceleration)

## Installation & Running

### Option 1: Docker (Recommended)

1.  **Build and Start**:
    ```bash
    docker-compose up --build
    ```
    *Note: The first run will download the model (~3GB) and base images.*

2.  **Access**: The server runs at `http://localhost:8000`.

### Option 2: Local Python

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run Server**:
    ```bash
    python server.py
    ```

## Configuration

You can configure the server using environment variables (in `.env` or `docker-compose.yml`):

| Variable | Description | Default |
| :--- | :--- | :--- |
| `TTS_MODEL_NAME` | Coqui TTS model name to load. | `tts_models/multilingual/multi-dataset/xtts_v2` |
| `DEFAULT_VOICE` | Default speaker filename (no ext) or name. | `default_speaker` |

## API Usage

### Endpoint: `POST /v1/audio/speech`

**Headers**: `Content-Type: application/json`

**Body Parameters**:

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `instructions` | string | Yes | The text to convert to speech. (Falls back to `input` for compatibility). |
| `voice` | string | No | Speaker identifier (see below). Defaults to `DEFAULT_VOICE`. |
| `language` | string | No | Language code (e.g., `en`, `ar`, `es`, `fr`). Default: `en`. |
| `model` | string | No | Ignored (for compatibility). |

### Speaker Selection (`voice` parameter)

The `voice` parameter is resolved in the following order:

1.  **Exact File**: Matches a file in `speakers/<voice>`.
2.  **Filename (no ext)**: Matches `speakers/<voice>.wav`.
3.  **Index**: If numeric (e.g., "0"), maps to the Nth file in `speakers/` (sorted alphabetically).
4.  **Speaker Name**: If no file is found, the value is passed directly to the model as a speaker name (useful for multi-speaker models without reference files).

### Example Request

```bash
curl http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1",
    "instructions": "Hello, this is a test of the TTS server.",
    "voice": "alloy",
    "language": "en"
  }' \
  --output output.wav
```

## Directory Structure

- `server.py`: Main server implementation.
- `speakers/`: Directory to store `.wav` reference files for voice cloning.
- `Dockerfile`: Docker build configuration.
- `docker-compose.yml`: Docker Compose configuration.
- `requirements.txt`: Python dependencies.
- `test_client.py`: Script to test the API.

## Adding Speakers

To add a new voice for cloning:
1.  Place a `.wav` file (e.g., `my_voice.wav`) in the `speakers/` directory.
2.  Use `voice: "my_voice"` in your API request.
