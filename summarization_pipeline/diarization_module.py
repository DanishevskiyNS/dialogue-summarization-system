from pyannote.audio import Pipeline
import torch

class DiarizationModule:
    def __init__(self, config):

        self.diarization_pipeline = Pipeline.from_pretrained(
            checkpoint_path=config.checkpoint_path,
            use_auth_token=config.hf_token)
        self.diarization_pipeline.to(torch.device(config.device))

    def diarize(self, audio_path: str, num_speakers: int | None = None) -> list[dict]:
        diarization = self.diarization_pipeline(audio_path, num_speakers)
        return self.format_diarization(diarization)
    
    def format_diarization(self, diarization: list[dict]) -> list[dict]:
        formatted_diarization = []
        for segment, track in diarization._tracks.items():
            formatted_diarization.append({
                "start": segment.start,
                "end": segment.end,
                "speacker_id": list(track.values())[0]
            })
        return formatted_diarization