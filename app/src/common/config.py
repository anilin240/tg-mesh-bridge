from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file="/app/.env", env_file_encoding="utf-8", extra="ignore")

    # MQTT
    mqtt_host: str = Field(default="192.168.50.81")
    mqtt_port: int = Field(default=1883)
    mqtt_user: str | None = None
    mqtt_pass: str | None = None
    mqtt_topic_sub: str = Field(default="msh/US/2/json/#", env="MQTT_TOPIC_SUB")
    mqtt_topic_pub: str = Field(default="msh/US/2/json/mqtt/", env="MQTT_TOPIC_PUB")

    # Postgres
    postgres_db: str = Field(default="tgmesh")
    postgres_user: str = Field(default="tgmesh")
    postgres_password: str = Field(default="changeme")
    postgres_host: str = Field(default="postgres")
    postgres_port: int = Field(default=5432)

    # Telegram
    bot_token: str | None = None


__all__ = ["AppConfig"]




