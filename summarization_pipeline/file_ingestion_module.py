import os
from pydub import AudioSegment
# import librosa
# import soundfile as sf

SUPPORTED_FORMATS = [".mp3", ".wav", ".m4a", ".flac", ".ogg", ".mp4"]

class FileIngestionModule:
    @staticmethod
    def preprocess_audio(file_path: str) -> str:
        """Предварительная обработка аудио"""
        if not FileIngestionModule.is_supported_format(file_path):
            raise ValueError(f"Unsupported file format: {file_path}")
        
        file_path = FileIngestionModule.convert_to_wav(file_path)
        normalized_path = FileIngestionModule.normalize_volume(file_path)
        resampled_path = FileIngestionModule.resample_audio(normalized_path)
        return resampled_path   
        
    def is_supported_format(self, file_path: str) -> bool:
        """Проверка, поддерживается ли формат."""
        return any(file_path.endswith(ext) for ext in SUPPORTED_FORMATS)
    
    def convert_to_wav(self, file_path: str) -> str:
        """Конвертация в WAV 16kHz mono"""
        if not self.is_supported_format(file_path):
            raise ValueError(f"Unsupported file format: {file_path}")
        
        # Конвертация в WAV
        wav_path = file_path.replace(os.path.splitext(file_path)[1], '.wav')
        audio = AudioSegment.from_file(file_path)
        audio.export(wav_path, format="wav")
        return wav_path
    
    def get_audio_metadata(self, file_path: str) -> dict:
        """Извлекает метаданные: длительность, частота, каналы и т.д."""
        
        audio = AudioSegment.from_file(file_path)
        return {
            "duration": len(audio) / 1000,
            "sample_rate": audio.frame_rate,
            "channels": audio.channels
        }

    def normalize_volume(self, audio_path: str) -> str:
        """Нормализация уровня громкости."""
        
        audio = AudioSegment.from_file(audio_path)
        audio = audio.normalize()
        return audio_path
        
    def resample_audio(self, audio_path: str, target_sr: int = 16000) -> str:
        """Ресемплирование аудио до нужной частоты."""
        audio = AudioSegment.from_wav(audio_path)
        resampled_audio = audio.set_frame_rate(target_sr)
        resampled_audio.export(audio_path, format="wav")
        return audio_path