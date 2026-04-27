"""结构化日志系统。"""
import logging
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from agent_system.config import settings


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        return json.dumps(log_data, ensure_ascii=False)


class PlainFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        return f"[{timestamp}] [{record.levelname}] [{record.name}] {record.getMessage()}"


def setup_logging(name: Optional[str] = None) -> logging.Logger:
    logger = logging.getLogger(name or "agent_system")
    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    if logger.handlers:
        return logger

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    if settings.log_json:
        console_handler.setFormatter(JsonFormatter())
    else:
        console_handler.setFormatter(PlainFormatter())

    logger.addHandler(console_handler)

    log_dir = Path(settings.log_dir)
    if not log_dir.exists() and log_dir.parent.exists():
        log_dir.mkdir(parents=True, exist_ok=True)

    if log_dir.exists() or log_dir.parent.exists():
        file_handler = logging.FileHandler(
            log_dir / f"agent_{datetime.now().strftime('%Y%m%d')}.log",
            encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(PlainFormatter())
        logger.addHandler(file_handler)

    return logger


logger = setup_logging("agent_system")