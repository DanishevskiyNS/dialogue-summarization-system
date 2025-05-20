import os
from pydantic import BaseModel

class DiarizationConfig(BaseModel):
    checkpoint_path: str
    hf_token: str

class TranscriptionConfig(BaseModel):
    type: str
    model_name: str

class SummarizationConfig(BaseModel):
    model: str
    url: str
    temperature: float
    format: str
    prompt_path: str
    
def load_transcription_config(language: str) -> TranscriptionConfig:
    if language == "ru":
        return TranscriptionConfig(type="gigaam", model_name=os.getenv("GIGAAM_MODEL_NAME"))
    else:
        return TranscriptionConfig(type="whisper", model_name=os.getenv("WHISPER_MODEL_NAME"))