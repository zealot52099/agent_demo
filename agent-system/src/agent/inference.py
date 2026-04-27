import re

# Mock 模式：不调用真实模型，根据 prompt 内容模拟输出
MOCK_MODE = True

# 域关键词映射
DOMAIN_KEYWORDS = {
    "导航控制域": ["导航", "路线", "充电站", "目的地", "地图", "途经", "路况", "红绿灯", "服务区"],
    "车窗控制域": ["车窗", "天窗", "遮阳帘", "天幕"],
    "声音控制域": ["音量", "声浪", "音效", "静音", "声音"],
    "座椅控制域": ["座椅", "加热", "通风", "按摩", "靠背", "腿托", "腰托"],
}

# 意图关键词映射（简化版）
INTENT_KEYWORDS = {
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


def _mock_inference(prompt, history=None):
    """根据 prompt 内容模拟模型输出"""
    # Stage 1: 域分类（prompt 中含"只输出域名"）
    if "只输出域名" in prompt:
        for domain, keywords in DOMAIN_KEYWORDS.items():
            for kw in keywords:
                if kw in prompt:
                    return domain
        return "导航控制域"  # 默认

    # Stage 2: 意图匹配（prompt 中含"ASR结果|意图名称"）
    if "意图名称" in prompt or "ASR结果" in prompt:
        for intent, keywords in INTENT_KEYWORDS.items():
            for kw in keywords:
                if kw in prompt:
                    # 提取用户原始 query
                    m = re.search(r"用户指令：(.+)", prompt)
                    query = m.group(1) if m else "未知"
                    return f"{query}|{intent}"
        return "未知指令|NoiseAction"

    return f"[Mock] 无法解析 prompt"


def run_inference(prompt, history=None, audio_url=None):
    """
    向推理服务发送请求（支持 mock 模式）
    """
    if MOCK_MODE:
        print(f"  [Mock] prompt 长度: {len(prompt)}")
        return _mock_inference(prompt, history)

    # --- 真实推理 ---
    import requests
    url = "http://localhost:8901/v1/chat/completions"
    headers = {"Content-Type": "application/json"}

    content = [{"type": "text", "text": prompt}]
    if audio_url:
        content.append({"type": "audio_url", "audio_url": {"url": audio_url}})

    messages = []
    if history:
        for h in history:
            messages.append({"role": "user", "content": h.get("query", "")})
            messages.append({"role": "assistant", "content": h.get("response", "")})
    messages.append({"role": "user", "content": content})

    payload = {"temperature": 0, "seed": 42, "messages": messages}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        print(f"请求出错: {e}")
        return None