from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='app/.env')

    MQTT_BROKER_URL: str
    MQTT_BROKER_PORT: int
    MQTT_SENSOR_TOPIC: str = "sensors"
    MQTT_COMMAND_TOPIC: str = "commands"

    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    WEATHER_API_URL: str = "https://api.tomorrow.io/v4/weather/forecast?"
    WEATHER_API_KEY: str


settings = Settings()
