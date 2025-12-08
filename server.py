import os
import litserve as ls
from TTS.api import TTS
import torch
import uuid

class XTTSV2API(ls.LitAPI):
    def setup(self, device):
        self.device = device
        
        # Read model name from ENV
        model_name = os.getenv("TTS_MODEL_NAME", "tts_models/multilingual/multi-dataset/xtts_v2")
        print(f"Loading XTTSv2 model '{model_name}' on {device}...")
        
        # Init TTS with the target model name
        self.tts = TTS(model_name).to(device)
        print("Model loaded successfully.")

    def decode(self, request):
        # OpenAI API compatible request structure
        # request is a dictionary from the JSON body
        
        # 1. Map 'instructions' to text (prompt), fallback to 'input'
        text = request.get("instructions")
        if not text:
            text = request.get("input", "Speak in a cheerful and positive tone.")
            
        # 2. Map 'voice' to 'speaker_ref' (string)
        # Use ENV default if not provided
        default_voice = os.getenv("DEFAULT_VOICE", "Craig Gutsy")
        speaker_ref = request.get("voice", default_voice)
        
        # 3. Language
        language = request.get("language", "en") # Default to English
        
        # Note: 'model' parameter is ignored as per requirements
        
        return {"text": text, "language": language, "speaker_ref": speaker_ref}

    def predict(self, inputs):
        text = inputs["text"]
        language = inputs["language"]
        speaker_ref = inputs["speaker_ref"]
        
        output_path = f"output_{uuid.uuid4()}.wav"
        
        # Speaker handling logic
        speakers_dir = "speakers"
        os.makedirs(speakers_dir, exist_ok=True)
        
        speaker_wav = None
        speaker = None
        
        # Resolve speaker_ref to a file
        # Priority 1: Exact filename match in speakers/
        if os.path.exists(os.path.join(speakers_dir, speaker_ref)):
             speaker_wav = os.path.join(speakers_dir, speaker_ref)
        
        # Priority 2: Match {speaker_ref}.wav
        elif os.path.exists(os.path.join(speakers_dir, f"{speaker_ref}.wav")):
             speaker_wav = os.path.join(speakers_dir, f"{speaker_ref}.wav")
             
        # Priority 3: If it looks like an index, try to use it as index
        elif speaker_ref.isdigit():
            try:
                idx = int(speaker_ref)
                speaker_files = sorted([f for f in os.listdir(speakers_dir) if f.endswith(".wav")])
                if 0 <= idx < len(speaker_files):
                    speaker_wav = os.path.join(speakers_dir, speaker_files[idx])
            except:
                pass
        
        if speaker_wav:
             print(f"Resolved speaker '{speaker_ref}' to wav file: {speaker_wav}")
             speaker = None
        else:
             # If speaker_ref is not a wav file (not found), then fill the speaker as same as speaker_ref value
             print(f"Speaker '{speaker_ref}' not found as file. Using as speaker name.")
             speaker = speaker_ref
             speaker_wav = None

        # Note: We removed the auto-download default logic because now any missing file is treated as a speaker name.
        # This assumes the user knows what they are doing (using a model that supports speaker names).
        
        if not speaker_wav and not speaker:
             # Should not happen given logic above (speaker becomes speaker_ref), but for safety:
             raise RuntimeError("No speaker reference available.")

        print(f"Generating TTS with language: {language}, speaker_wav: {speaker_wav}, speaker: {speaker}")
        self.tts.tts_to_file(
            text=text, 
            speaker_wav=speaker_wav, 
            language=language, 
            file_path=output_path,
            speaker=speaker
        )
        
        return output_path

    def encode(self, output_path):
        # Stream the file back? Or just return it.
        # LitServe supports streaming response?
        # For now, let's return the file content.
        # But OpenAI API returns binary audio.
        
        with open(output_path, "rb") as f:
            audio_data = f.read()
        
        # Clean up
        os.remove(output_path)
        
        return audio_data

if __name__ == "__main__":
    # We need to map the OpenAI endpoint
    # OpenAI TTS endpoint: POST https://api.openai.com/v1/audio/speech
    api = XTTSV2API()
    server = ls.LitServer(api, api_path="/v1/audio/speech")
    server.run(port=8000)
