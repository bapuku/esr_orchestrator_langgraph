from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    insurer_api_base: str = os.getenv("INSURER_API_BASE", "https://api.mockinsurer.local")
    insurer_api_key: str | None = os.getenv("INSURER_API_KEY")

settings = Settings()
