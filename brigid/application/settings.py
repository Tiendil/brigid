import pydantic
import pydantic_settings

from brigid.core.settings import BaseSettings


class Sentry(pydantic.BaseModel):
    enabled: bool = False
    dsn: str = ""
    sample_rate: float = 1.0
    enable_tracing: bool = False
    traces_sample_rate: float = 1.0


_development_origins = ("*",)


class Settings(BaseSettings):
    environment: str = "local"

    sentry: Sentry = Sentry()

    origins: tuple[str, ...] = _development_origins

    @pydantic.model_validator(mode="after")
    def origin_must_be_redefined_in_prod(self) -> "Settings":
        if self.environment == "prod" and self.origins == _development_origins:
            raise ValueError("Origins must be redefined in prod")

        return self

    model_config = pydantic_settings.SettingsConfigDict(env_prefix="BRIGID_")


settings = Settings()
