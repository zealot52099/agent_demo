"""模型输出的结构化契约。"""
from typing import Optional
from pydantic import BaseModel, Field, field_validator
import re


class IntentResult(BaseModel):
    """单个意图解析结果。"""
    asr_text: str = Field(..., description="识别出的文本")
    intent: str = Field(..., description="API 意图名称")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    domain: Optional[str] = None
    raw_output: Optional[str] = None  # 保留原始输出便于调试

    @field_validator("intent")
    @classmethod
    def _intent_format(cls, v: str) -> str:
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", v):
            raise ValueError(f"非法意图名: {v}")
        return v

    @classmethod
    def parse_pipe_format(cls, raw: str, domain: Optional[str] = None) -> "IntentResult":
        """解析 'ASR文本|IntentName' 格式，带兜底。"""
        text = raw.strip()
        # 容错：去掉 <answer></answer> 之类标签
        text = re.sub(r"<[^>]+>", "", text).strip()
        if "|" not in text:
            return cls(asr_text=text, intent="NoiseAction",
                       confidence=0.0, domain=domain, raw_output=raw)
        asr, intent = text.rsplit("|", 1)
        try:
            return cls(asr_text=asr.strip(), intent=intent.strip(),
                       domain=domain, raw_output=raw)
        except ValueError:
            return cls(asr_text=asr.strip(), intent="NoiseAction",
                       confidence=0.0, domain=domain, raw_output=raw)
