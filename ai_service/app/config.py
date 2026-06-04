from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


WORKSPACE_DIR = Path(__file__).resolve().parents[2]

for env_file_path in (WORKSPACE_DIR / '.env', WORKSPACE_DIR / 'config' / '.env'):
    if env_file_path.exists():
        load_dotenv(env_file_path)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra='ignore')

    database_url: str = Field(default='sqlite:///./ai_service.sqlite3', alias='DATABASE_URL')
    openai_api_key: str | None = Field(default=None, alias='OPENAI_API_KEY')
    openai_model: str = Field(default='gpt-4.1-mini', alias='OPENAI_MODEL')
    openai_use_mock: bool = Field(default=False, alias='OPENAI_USE_MOCK')

    @property
    def has_real_openai_key(self):
        if not self.openai_api_key:
            return False
        return self.openai_api_key not in {'your_api_key_here', 'change-me'}


@lru_cache
def get_settings():
    return Settings()
