from pydantic import BaseSettings, Field


class StorageConfig(BaseSettings):
    BUCKET_NAME: str = Field(default="", env="S3_BUCKET_NAME")
    ACCESS_KEY: str = Field(default="", env="S3_ACCESS_KEY")
    SECRET_KEY: str = Field(default="", env="S3_SECRET_KEY")
    REGION: str = Field(default="", env="S3_REGION")

    class Config:
        env_file = ".env"
        case_sensitive = True


