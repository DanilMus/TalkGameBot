from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, Secret


# Создаем тип SecretInt
SecretInt = Secret[int]

class Settings(BaseSettings):
    bot_token: SecretStr # токен бота

    id_owner: SecretInt # id владельца всего этого дела

    db_user: SecretStr
    db_password: SecretStr
    db_host: SecretStr
    db_name: SecretStr

    model_config = SettingsConfigDict(env_file= "config/config.env", env_file_encoding= "utf-8")


config = Settings()