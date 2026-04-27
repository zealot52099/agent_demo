"""推理模块 - 支持 Mock/真实 LLM 推理。"""
import re
import time
from typing import Optional, List, Dict, Any, Union

import requests
from requests.exceptions import RequestException

from agent_system.config import settings
from agent_system.logging_config import logger


class InferenceError(Exception):
    pass


class ValidationError(InferenceError):
    pass


def _mock_inference(prompt: str, history: Optional[List[Dict]] = None) -> str:
    """Mock 模式：根据 prompt 内容模拟模型输出"""
    domain_keywords = {
        "导航控制域": ["导航", "路线", "充电站", "目的地", "地图", "途经", "路况", "红绿灯", "服务区"],
        "车窗控制域": ["车窗", "天窗", "遮阳帘", "天幕"],
        "声音控制域": ["音量", "声浪", "音效", "静音", "声音"],
        "座椅控制域": ["座椅", "加热", "通风", "按摩", "靠背", "腿托", "腰托"],
    }

    intent_keywords = {
        "NavigationSearchPoi": ["导航到", "去", "搜索", "找"],
        "NavigationSearchCharging": ["充电站", "充电"],
        "NavigationExit": ["退出导航", "关闭导航"],
        "NavigationSetRoutePrefer": ["高速优先", "避开拥堵", "路线偏好"],
        "WindowsOpen": ["打开车窗", "开窗", "打开天窗"],
        "WindowsClose": ["关闭车窗", "关窗", "关闭天窗"],
        "WindowsSet": ["车窗开到", "车窗调"],
        "VoiceSet": ["音量调", "调大音量", "调小音量"],
        "VoiceOpen": ["打开声浪", "打开音效"],
        "VoiceClose": ["关闭声浪", "关闭音效"],
        "SeatOpen": ["打开座椅", "开启座椅", "座椅加热", "座椅通风", "座椅按摩"],
        "SeatClose": ["关闭座椅", "关座椅"],
        "SeatSet": ["座椅调", "靠背调"],
    }

    if "只输出域名" in prompt:
        for domain, keywords in domain_keywords.items():
            for kw in keywords:
                if kw in prompt:
                    logger.debug(f"Mock domain matched: {domain}")
                    return domain
        return "导航控制域"

    if "意图名称" in prompt or "ASR结果" in prompt:
        for intent, keywords in intent_keywords.items():
            for kw in keywords:
                if kw in prompt:
                    m = re.search(r"用户指令：(.+)", prompt)
                    query = m.group(1) if m else "未知"
                    result = f"{query}|{intent}"
                    logger.debug(f"Mock intent matched: {result}")
                    return result
        return "未知指令|NoiseAction"

    return f"[Mock] 无法解析 prompt"


def _real_inference(
    prompt: str,
    history: Optional[List[Dict]] = None,
    audio_url: Optional[str] = None
) -> Optional[str]:
    """真实 LLM 推理调用"""
    url = settings.inference_url
    headers = {"Content-Type": "application/json"}

    content = [{"type": "text", "text": prompt}]
    if audio_url:
        content.append({"type": "audio_url", "audio_url": {"url": audio_url}})

    messages = []
    if history:
        for h in history:
            # logger.info(f"Adding history to inference payload: {h}")
            if isinstance(h, dict):
                if h.get("query", "") and h.get("response", ""):
                    messages.append({"role": "user", "content": h.get("query", "")})
                    messages.append({"role": "assistant", "content": h.get("response", "")})
    if content:
        messages.append({"role": "user", "content": content})
    logger.info(f'messages for inference: {messages}')
    payload = {
        "temperature": settings.inference_temperature,
        "seed": settings.inference_seed,
        "messages": messages
    }

    retry_count = 0
    last_error = None

    while retry_count <= settings.inference_max_retries:
        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=settings.inference_timeout
            )
            response.raise_for_status()
            result = response.json()

            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0].get("message", {}).get("content", "")
                logger.info(f"Inference success, response length: {len(content)}")
                return content
            else:
                logger.warning(f"Unexpected inference response format: {result}")
                return None

        except RequestException as e:
            last_error = e
            retry_count += 1
            logger.warning(f"Inference request failed (attempt {retry_count}): {e}")
            if retry_count <= settings.inference_max_retries:
                time.sleep(1 * retry_count)

    logger.error(f"Inference failed after {settings.inference_max_retries} retries: {last_error}")
    return None


def run_inference(
    prompt: str,
    history: Optional[List[Dict]] = None,
    audio_url: Optional[str] = None
) -> str:
    """
    向推理服务发送请求（支持 Mock/真实模式）

    Args:
        prompt: 推理 prompt
        history: 对话历史
        audio_url: 音频 URL（可选）

    Returns:
        模型输出字符串
    """
    if settings.mock_mode:
        logger.debug("Running in mock mode")
        return _mock_inference(prompt, history)

    logger.debug("Running in real inference mode")
    result = _real_inference(prompt, history, audio_url)
    if result is None:
        raise InferenceError("LLM inference failed")
    return result


def run_inference_with_fallback(
    prompt: str,
    history: Optional[List[Dict]] = None,
    audio_url: Optional[str] = None
) -> str:
    """
    带有降级策略的推理：真实推理失败时自动降级到 Mock
    """
    if settings.mock_mode:
        return _mock_inference(prompt, history)

    # try:
    result = _real_inference(prompt, history, audio_url)
    if result:
        return result
    logger.warning("Real inference failed, falling back to mock")
    return _mock_inference(prompt, history)
    # except Exception as e:
    #     logger.error(f"Real inference error: {e}, falling back to mock")
    #     return _mock_inference(prompt, history)