from typing import Dict, Any

# API definitions for the inference requests
API_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "chat_completions": {
        "url": "http://localhost:8901/v1/chat/completions",
        "method": "POST",
        "headers": {
            "Content-Type": "application/json"
        },
        "payload_structure": {
            "temperature": 0,
            "seed": 42,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "string"  # Placeholder for user text input
                        },
                        {
                            "type": "audio_url",
                            "audio_url": {
                                "url": "string"  # Placeholder for audio file URL
                            }
                        },
                        {
                            "type": "text",
                            "text": "string"  # Placeholder for additional text input
                        }
                    ]
                }
            ]
        }
    }
}

def get_api_definition(api_name: str) -> Dict[str, Any]:
    """Retrieve the API definition by name."""
    return API_DEFINITIONS.get(api_name, {})