import boto3
import os
from botocore.exceptions import ClientError
from typing import Optional



class StorageManager:
    def __init__(self, config):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=config.ACCESS_KEY,
            aws_secret_access_key=config.SECRET_KEY,
            region_name=config.REGION
        )
        self.bucket_name = config.BUCKET_NAME

    def upload_file(self, file_path: str, s3_key: str) -> bool:
        try:
            self.s3_client.upload_file(file_path, self.bucket_name, s3_key)
            return True
        except ClientError as e:
            print(f"Error uploading file to S3: {e}")
            return False

    def get_download_url(self, s3_key: str, expiration: int = 3600) -> Optional[str]:
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            print(f"Error generating download URL: {e}")
            return None

# Initialize S3 storage with bucket name from environment variable
s3_storage = StorageManager(os.getenv('S3_BUCKET_NAME', 'your-bucket-name')) 