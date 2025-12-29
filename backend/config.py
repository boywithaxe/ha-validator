from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    HA_URL: str = "http://localhost:8123"
    HA_TOKEN: str = "change_me"

    class Config:
        env_file = ".env"

settings = Settings()
