import os
import io
import json
import litserve as ls
import uuid

from TTS.api import TTS
from fastapi.responses import Response
from pydub import AudioSegment
import torch

os.environ["COQUI_TOS_AGREED"] = "1"
use_cuda = torch.cuda.is_available()


class XTTSV2API(ls.LitAPI):
    def setup(self, device):
        self.device = device

        # Load list of allowed TTS models from JSON config
        config_path = os.getenv("TTS_MODELS_CONFIG", "tts_models.json")
        if not os.path.exists(config_path):
            raise RuntimeError(
                f"TTS models config file '{config_path}' not found. "
                "Create it (e.g. via tts_models.json) with a JSON array of model configs."
            )

        with open(config_path, "r", encoding="utf-8") as f:
            try:
                raw_models = json.load(f)
            except json.JSONDecodeError as e:
                raise RuntimeError(
                    f"Failed to parse TTS models config '{config_path}': {e}"
                )

        if not isinstance(raw_models, list) or not raw_models:
            raise RuntimeError(
                f"TTS models config '{config_path}' must be in valid JSON format."
            )

        # register models
        model_configs = []
        for idx, item in enumerate(raw_models):
            model_configs.append(
                {
                    "model_name": item["model_name"],
                    "default_voice": item["default_voice"],
                }
            )

        model_names = [cfg["model_name"] for cfg in model_configs]

        # Optional default model name, must be one of the configured models
        default_model_name = os.getenv("DEFAULT_TTS_MODEL_NAME")
        default_voice = os.getenv("DEFAULT_VOICE")
        if default_model_name and default_model_name not in model_names:
            model_configs.append(
                {
                    "model_name": default_model_name,
                    "default_voice": default_voice,
                }
            )

        self.models = {}
        self.model_default_voices = {}
        for cfg in model_configs:
            name = cfg["model_name"]
            print(f"Loading TTS model '{name}' on {device}...")
            self.models[name] = TTS(name).to(device)
            self.model_default_voices[name] = cfg.get("default_voice")

        self.default_model_name = default_model_name

    def decode_request(self, request):
        # OpenAI API compatible request structure
        # request is a dictionary from the JSON body

        # 0. Model selection (REQUIRED and must be one of the preloaded models)
        model_name = request.get("model")
        if model_name is None:
            raise ValueError("Missing 'model' field in request body.")
        if model_name not in self.models:
            raise ValueError(
                f"Requested model '{model_name}' is not available. "
                f"Available models: {list(self.models.keys())}"
            )

        # 1. Text input
        text = request.get("input")
        if text is None or text == "":
            raise ValueError("Missing or empty 'input' text field in request body.")

        # 2. Map 'voice' to 'speaker_ref' (string)
        # Priority: explicit request voice > per-model default > env default
        request_voice = request.get("voice")
        if request_voice is not None:
            speaker_ref = request_voice
        else:
            model_default_voice = getattr(self, "model_default_voices", {}).get(
                model_name
            )
            if model_default_voice:
                speaker_ref = model_default_voice
            else:
                speaker_ref = os.getenv("DEFAULT_VOICE", "Craig Gutsy")

        # 3. Language
        language = request.get("instructions", "en")  # Default to English

        return {
            "model_name": model_name,
            "text": text,
            "language": language,
            "speaker_ref": speaker_ref,
            "response_format": request.get("response_format", "mp3"),
        }

    def predict(self, inputs):
        model_name = inputs["model_name"]
        tts = self.models[model_name]

        text = inputs["text"]
        language = inputs["language"]
        speaker_ref = inputs["speaker_ref"]

        output_path = f"output/output_{uuid.uuid4()}.wav"

        # Speaker handling logic
        speakers_dir = "speakers"
        os.makedirs(speakers_dir, exist_ok=True)

        speaker_wav = None
        speaker = None

        # Resolve speaker_ref to a file
        # Priority 1: If speaker_ref already looks like a path, try it directly.
        if os.path.isabs(speaker_ref) or os.path.sep in speaker_ref:
            if os.path.exists(speaker_ref):
                speaker_wav = speaker_ref

        # Priority 2: Exact filename match in speakers/
        if speaker_wav is None and os.path.exists(
            os.path.join(speakers_dir, speaker_ref)
        ):
            speaker_wav = os.path.join(speakers_dir, speaker_ref)

        # Priority 3: Match {speaker_ref}.wav
        if speaker_wav is None and os.path.exists(
            os.path.join(speakers_dir, f"{speaker_ref}.wav")
        ):
            speaker_wav = os.path.join(speakers_dir, f"{speaker_ref}.wav")

        if speaker_wav:
            print(f"Resolved speaker '{speaker_ref}' to wav file: {speaker_wav}")
            speaker = None
        else:
            # If speaker_ref is not a wav file (not found), then fill the speaker as same as speaker_ref value
            print(f"Speaker '{speaker_ref}' not found as file. Using as speaker name.")
            speaker = speaker_ref
            speaker_wav = None

        if not speaker_wav and not speaker:
            raise RuntimeError("No speaker reference available.")

        if "multi" not in model_name:
            language = None

        print(
            f"Generating TTS '{text}' with model: {model_name}, language: {language}, speaker_wav: {speaker_wav}, speaker: {speaker}"
        )
        tts.tts_to_file(
            text=text,
            speaker_wav=speaker_wav,
            language=language,
            file_path=output_path,
            speaker=speaker,
        )

        return {
            "output_path": output_path,
            "response_format": inputs["response_format"],
        }

    def encode_response(self, outputs):
        # Return the file content.
        response_format = outputs["response_format"]
        output_path = outputs["output_path"]

        audio = AudioSegment.from_wav(output_path)
        buffer = io.BytesIO()
        audio.export(buffer, format=response_format)

        # Clean up
        os.remove(output_path)

        media_type = f"audio/{str(response_format).lower()}"

        if response_format == "mp3":
            media_type = "audio/mpeg"

        return Response(
            content=buffer.getvalue(),
            media_type=media_type,
        )


if __name__ == "__main__":
    accelerator = "gpu" if use_cuda else "auto"

    api = XTTSV2API(api_path="/v1/audio/speech")
    server = ls.LitServer(api, accelerator=accelerator)
    server.run(port=os.getenv("PORT", 8000), generate_client_file=False)
