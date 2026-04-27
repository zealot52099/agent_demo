"""集中配置：通过环境变量 / .env 覆盖，避免硬编码。"""
import os
from functools import lru_cache
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        env_file_encoding="utf-8",
        env_prefix="AGENT_",
        case_sensitive=False
    )

    # 推理服务
    inference_url: str = Field(default="http://localhost:8901/v1/chat/completions")
    inference_timeout: float = Field(default=30.0)
    inference_max_retries: int = Field(default=2)
    inference_temperature: float = Field(default=0)
    inference_seed: int = Field(default=42)

    # 行为开关
    mock_mode: bool = Field(default=False)
    enable_two_stage: bool = Field(default=True)
    enable_vector_recall: bool = Field(default=False)

    # 上下文管理
    max_history_turns: int = Field(default=5)
    max_prompt_tokens: int = Field(default=8000)

    # 日志
    log_level: str = Field(default="INFO")
    log_json: bool = Field(default=False)
    log_dir: str = Field(default="logs")

    # 服务
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)


@lru_cache
def get_settings() -> Settings:
    return Settings()


def clear_settings_cache():
    get_settings.cache_clear()


settings = get_settings()