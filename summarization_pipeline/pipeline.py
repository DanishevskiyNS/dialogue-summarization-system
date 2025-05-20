from concurrent.futures import ProcessPoolExecutor

from file_ingestion_module import FileIngestionModule
from transcription_module import TranscriptionModule
from diarization_module import DiarizationModule
from dialogue_parser_module import DialogueParserModule
from summarization_module import SummarizationModule
from result_formatter import ResultFormatterModule
from config import load_transcription_config


class SummarizationPipeline:
    def __init__(self, transcription_config, diarization_config, summarization_config, status_tracker, num_speakers, language):
        transcription_module = load_transcription_config(language)
        self.transcription = TranscriptionModule.from_config(transcription_module)
        self.diarization = DiarizationModule(diarization_config)
        self.summarization = SummarizationModule(summarization_config)
        self.status_tracker = status_tracker
        self.num_speakers = num_speakers
        self.language = language
    
    def run(self, audio_file_path, task_id):
        # 1. File ingestion
        FileIngestionModule.preprocess_audio(audio_file_path)
        self.status_tracker.set_status(task_id, "preprocessed")
        
        # 2. Transcription 
        transcription = self.transcription.transcribe(audio_file_path)
        self.status_tracker.set_status(task_id, "transcription_done")
        
        # 3. Diarization
        diarization = self.diarization.diarize(audio_file_path, self.num_speakers)
        self.status_tracker.set_status(task_id, "diarization_done")
        
        # 4. Dialogue parsing
        dialogue = DialogueParserModule.format_as_dialogue(transcription, diarization)
        self.status_tracker.set_status(task_id, "dialogue_done")

        # 5. Summarization
        summary = self.summarization.summarize(dialogue)
        self.status_tracker.set_status(task_id, "summarization_done")

        # 6. Formatting
        formatted_summary = ResultFormatterModule.format_results(summary)
        self.status_tracker.set_status(task_id, "formatting_done")

        return formatted_summary
    
    