from __future__ import annotations
from pathlib import Path
from dotenv import dotenv_values
from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)
import logging
import automationassets
from automationassets import AutomationAssetNotFound

logger = logging.getLogger(__name__)


class AzureCustomSource(EnvSettingsSource):
    def _get_config(self) -> dict[str, str]:
        env_var = self._read_env_file()
        return {
            "access_token": env_var.get("CLOUD_SYNC__ACCESS_TOKEN")
            if "CLOUD_SYNC__ACCESS_TOKEN" in env_var
            else automationassets.get_automation_variable("CLOUD_SYNC__ACCESS_TOKEN"),
            "zivver_api_key": env_var.get("CLOUD_SYNC__ZIVVER_API_KEY")
            if "CLOUD_SYNC__ZIVVER_API_KEY" in env_var
            else automationassets.get_automation_variable("CLOUD_SYNC__ZIVVER_API_KEY"),
            "zivver_api_url": env_var.get("CLOUD_SYNC__ZIVVER_API_URL")
            if "CLOUD_SYNC__ZIVVER_API_URL" in env_var
            else automationassets.get_automation_variable("CLOUD_SYNC__ZIVVER_API_URL"),
            "zivver_claimed_domains": env_var.get(
                "CLOUD_SYNC__ZIVVER_CLAIMED_DOMAINS"
            ).split(",")
            if "CLOUD_SYNC__ZIVVER_CLAIMED_DOMAINS" in env_var
            else automationassets.get_automation_variable(
                "CLOUD_SYNC__ZIVVER_CLAIMED_DOMAINS"
            ),
        }

    def _read_env_file(self) -> dict[str, str | None]:
        env_path = Path(self.config.get("env_file")).expanduser()
        if env_path.is_file():
            return dotenv_values(dotenv_path=env_path, verbose=True, interpolate=True)
        return {}

    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> tuple[any, str, bool]:
        field_value = self._get_config().get(field_name)
        return field_value, field_name, False

    def prepare_field_value(
        self, field_name: str, field: FieldInfo, value: any, value_is_complex: bool
    ) -> any:
        return value

    def decode_complex_value(
        self, field_name: str, field: FieldInfo, value: any
    ) -> any:
        raise NotImplementedError("AzureCustomSource does not support complex values")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_prefix="CLOUD_SYNC__"
    )

    access_token: str
    zivver_api_key: str
    zivver_api_url: str
    zivver_claimed_domains: list[str]

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: BaseSettings,
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            AzureCustomSource(settings_cls),
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )
