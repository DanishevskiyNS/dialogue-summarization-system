from celery import Celery
import os
from typing import Dict
from s3_storage import s3_storage
from status_tracker import status_tracker
from summarization_pipeline import SummarizationPipeline

celery_app = Celery("audio_tasks", broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'))

@celery_app.task(bind=True)
def process_audio_task(self, filepath: str, task_id: str, num_speakers: int | None, language: str | None):
    pipeline = SummarizationPipeline()
    try:
        # Обновляем статус
        status_tracker.set_status(task_id, "processing", {"filename": os.path.basename(filepath)})
        
        # Запускаем пайплайн
        result = pipeline.run(filepath, num_speakers, language)

        # Загружаем оба отформатированных файла в S3
        s3_keys = {}
        for file_type, file_path in result.items():
            s3_key = f"results/{task_id}/{os.path.basename(file_path)}"
            if s3_storage.upload_file(file_path, s3_key):
                s3_keys[file_type] = s3_key
            else:
                raise Exception(f"Failed to upload {file_type} file to S3")
        
        # Обновляем статус
        status_tracker.set_status(
            task_id,
            "completed",
            {
                "filename": os.path.basename(filepath),
                "s3_keys": s3_keys
            }
        )
        
        # Удаляем локальные файлы
        if os.path.exists(filepath):
            os.remove(filepath)
        for file_path in result.values():
            if os.path.exists(file_path):
                os.remove(file_path)
            
        return {"status": "completed"}
        
    except Exception as e:
        status_tracker.set_status(
            task_id,
            "failed",
            {
                "error": str(e),
                "filename": os.path.basename(filepath)
            }
        )
        self.retry(exc=e, countdown=60, max_retries=3)