from pydantic_settings import BaseSettings, SettingsConfigDict


class Setting(BaseSettings):
    database_url: str

    model_config = SettingsConfigDict( env_file="../.env", env_file_encoding="utf-8", extra="ignore")


settings = Setting()