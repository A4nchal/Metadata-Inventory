from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongo_uri: str = Field(..., alias="MONGO_URI")
    db_name: str = Field(..., alias="DB_NAME")
    request_timeout: int = Field(default=10, alias="REQUEST_TIMEOUT")

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()