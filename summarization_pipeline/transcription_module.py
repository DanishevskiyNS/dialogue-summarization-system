
import os
import abc

import whisper
import gigaam

import torch
import torchaudio
from pyannote.audio import Pipeline


class TranscriptionModule(abc.ABC):
    @abc.abstractmethod
    def transcribe(self, audio_path: str) -> list[dict]:
        """
        Возвращает список сегментов c речью
        """
        pass
    
    @abc.abstractmethod
    def format_transcription(self, transcription_segments: list[dict]) -> str:
        """Извлекает сплошной текст из сегментов."""
        pass

    @staticmethod
    def from_config(config) -> "TranscriptionModule":
        if config.type == "gigaam":
            return GigaamTranscriptionModule(config)
        elif config.type == "whisper":
            return WhisperTranscriptionModule(config)
        else:
            raise ValueError(f"Unknown model type: {config.model_name}")

class GigaamTranscriptionModule(TranscriptionModule):
    def __init__(self, config):
        self.model = gigaam.load_model(config.model_name)
        self.energy_threshold = config.energy_threshold
        self.pipeline = Pipeline.from_pretrained("pyannote/voice-activity-detection", use_auth_token=config.hf_token)

        os.makedirs("temp_chunks", exist_ok=True)
    
    def transcribe(self, audio_path: str) -> list[dict]:
        waveform, sr, active_segments = self.vad(audio_path)

        chunks = []
        for segment in active_segments:
            start = segment["start"]
            end = segment["end"]
            chunk_tensor = waveform[:, start:end].to(self.model._device).to(self.model._dtype)
            transcription = self.run_model(chunk_tensor)
            chunks.append({
                "start": start / sr,
                "end": end / sr,
                "transcription": transcription
            })

        return self.format_transcription(chunks)
    
    def run_model(self, chunk_tensor: torch.Tensor) -> str:
        length_tensor = torch.full([1], chunk_tensor.shape[-1], device=self.model._device)

        if length_tensor.item() > self.model.LONGFORM_THRESHOLD:
            # Process long audio in chunks
            chunk_size = self.model.LONGFORM_THRESHOLD
            num_chunks = (length_tensor.item() + chunk_size - 1) // chunk_size
            transcription = ""
            
            for i in range(num_chunks):
                start = i * chunk_size
                end = min(start + chunk_size, length_tensor.item())
                chunk = chunk_tensor[:, start:end]
                chunk_len = torch.full([1], chunk.shape[-1], device=self.model._device)
                
                chunk_encoded, chunk_encoded_len = self.model.forward(chunk, chunk_len)
                transcription += self.model.decoding.decode(self.model.head, chunk_encoded, chunk_encoded_len)[0]
                
        else:
            encoded, encoded_len = self.model.forward(chunk_tensor, length_tensor)  
            transcription = self.model.decoding.decode(self.model.head, encoded, encoded_len)[0]
        return transcription
    
    def vad(self, audio_path: str) -> list[dict]:
        # pyannote работает напрямую с файлом
        vad_result = self.pipeline(audio_path)

        # Загружаем аудио для возврата, если нужно
        waveform, sr = torchaudio.load(audio_path)
        if sr != 16000:
            waveform = torchaudio.functional.resample(waveform, sr, 16000)
            sr = 16000

        # Преобразуем сегменты в list[dict]
        speech_segments = []
        for turn in vad_result.get_timeline().support():
            speech_segments.append({
                "start": int(turn.start * sr),
                "end": int(turn.end * sr)
            })

        return waveform[0], sr, speech_segments

    
    def format_transcription(self, transcription_segments: list[dict]) -> str:
        return transcription_segments
    

class WhisperTranscriptionModule(TranscriptionModule):
    def __init__(self, config):
        self.model = whisper.load_model(config.model_name)

    def transcribe(self, audio_path: str) -> list[dict]:
        return self.format_transcription(self.model.transcribe(audio_path))

    def format_transcription(self, transcription_segments: list[dict]) -> str:
        return transcription_segments