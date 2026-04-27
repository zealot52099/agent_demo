"""集中配置：通过环境变量 / .env 覆盖，避免硬编码。"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="AGENT_")

    # 推理服务
    inference_url: str = "http://localhost:8901/v1/chat/completions"
    inference_timeout: float = 30.0
    inference_max_retries: int = 2

    # 行为开关
    mock_mode: bool = True
    enable_two_stage: bool = True
    enable_vector_recall: bool = False

    # 上下文管理
    max_history_turns: int = 5
    max_prompt_tokens: int = 8000

    # 日志
    log_level: str = "INFO"
    log_json: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
