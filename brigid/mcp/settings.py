import pydantic
import pydantic_settings

from brigid.core.settings import BaseSettings


class Settings(BaseSettings):
    name: str = "Blog MCP"

    model_config = pydantic_settings.SettingsConfigDict(env_prefix="BRIGID_MCP_")


settings = Settings()
