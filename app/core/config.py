from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    OPENAI_API_KEY: str = "your_key_here"

    # class Config:
    #     env_file = ".env"
    #     extra = "allow"
    model_config = {
        "env_file": ".env",
        "extra": "allow"
    }

settings = Settings()
