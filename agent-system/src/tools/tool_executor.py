"""Tool 执行层。"""
import re
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

from agent_system.logging_config import logger
from agent_system.agent.schema import IntentResult


class ExecuteStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    PENDING = "pending"


@dataclass
class ToolResult:
    status: ExecuteStatus
    tool_name: str
    result: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "status": self.status.value,
            "tool_name": self.tool_name,
            "result": self.result,
            "error": self.error,
            "metadata": self.metadata
        }


class Tool:
    def __init__(self, name: str, description: str, parameters: Optional[Dict] = None):
        self.name = name
        self.description = description
        self.parameters = parameters or {}

    def execute(self, params: Dict) -> ToolResult:
        raise NotImplementedError

    def validate_params(self, params: Dict) -> bool:
        for required in self.parameters.get("required", []):
            if required not in params:
                return False
        return True


class NavigationTools:
    NAVIGATION_TOOLS: Dict[str, Callable] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(func: Callable):
            cls.NAVIGATION_TOOLS[name] = func
            return func
        return decorator

    @classmethod
    def execute(cls, tool_name: str, params: Dict) -> ToolResult:
        if tool_name not in cls.NAVIGATION_TOOLS:
            return ToolResult(
                status=ExecuteStatus.FAILED,
                tool_name=tool_name,
                result=None,
                error=f"Unknown tool: {tool_name}"
            )
        try:
            result = cls.NAVIGATION_TOOLS[tool_name](**params)
            logger.info(f"Executed tool {tool_name}, result: {result}")
            return ToolResult(
                status=ExecuteStatus.SUCCESS,
                tool_name=tool_name,
                result=result
            )
        except Exception as e:
            logger.error(f"Tool {tool_name} failed: {e}")
            return ToolResult(
                status=ExecuteStatus.FAILED,
                tool_name=tool_name,
                result=None,
                error=str(e)
            )


@NavigationTools.register("NavigationSearchPoi")
def search_poi(poi_name: str, poi_type: Optional[str] = None, **kwargs):
    logger.info(f"Searching POI: {poi_name}, type: {poi_type}")
    return {"action": "search_poi", "poi_name": poi_name, "poi_type": poi_type, "status": "executed"}


@NavigationTools.register("NavigationSetDestination")
def set_destination(destination: str, **kwargs):
    logger.info(f"Setting destination: {destination}")
    return {"action": "set_destination", "destination": destination, "status": "executed"}


@NavigationTools.register("NavigationExit")
def exit_navigation(**kwargs):
    logger.info("Exiting navigation")
    return {"action": "exit_navigation", "status": "executed"}


@NavigationTools.register("NavigationSetRoutePrefer")
def set_route_prefer(prefer_type: str, **kwargs):
    logger.info(f"Setting route prefer: {prefer_type}")
    return {"action": "set_route_prefer", "prefer_type": prefer_type, "status": "executed"}


class WindowTools:
    WINDOW_TOOLS: Dict[str, Callable] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(func: Callable):
            cls.WINDOW_TOOLS[name] = func
            return func
        return decorator

    @classmethod
    def execute(cls, tool_name: str, params: Dict) -> ToolResult:
        if tool_name not in cls.WINDOW_TOOLS:
            return ToolResult(
                status=ExecuteStatus.FAILED,
                tool_name=tool_name,
                result=None,
                error=f"Unknown tool: {tool_name}"
            )
        try:
            result = cls.WINDOW_TOOLS[tool_name](**params)
            return ToolResult(
                status=ExecuteStatus.SUCCESS,
                tool_name=tool_name,
                result=result
            )
        except Exception as e:
            return ToolResult(
                status=ExecuteStatus.FAILED,
                tool_name=tool_name,
                result=None,
                error=str(e)
            )


@WindowTools.register("WindowsOpen")
def open_windows(window_type: str = "all", **kwargs):
    return {"action": "windows_open", "window_type": window_type, "status": "executed"}


@WindowTools.register("WindowsClose")
def close_windows(window_type: str = "all", **kwargs):
    return {"action": "windows_close", "window_type": window_type, "status": "executed"}


@WindowTools.register("WindowsSet")
def set_windows(position: int, window_type: str = "all", **kwargs):
    return {"action": "windows_set", "window_type": window_type, "position": position, "status": "executed"}


class VoiceTools:
    VOICE_TOOLS: Dict[str, Callable] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(func: Callable):
            cls.VOICE_TOOLS[name] = func
            return func
        return decorator

    @classmethod
    def execute(cls, tool_name: str, params: Dict) -> ToolResult:
        if tool_name not in cls.VOICE_TOOLS:
            return ToolResult(
                status=ExecuteStatus.FAILED,
                tool_name=tool_name,
                result=None,
                error=f"Unknown tool: {tool_name}"
            )
        try:
            result = cls.VOICE_TOOLS[tool_name](**params)
            return ToolResult(
                status=ExecuteStatus.SUCCESS,
                tool_name=tool_name,
                result=result
            )
        except Exception as e:
            return ToolResult(
                status=ExecuteStatus.FAILED,
                tool_name=tool_name,
                result=None,
                error=str(e)
            )


@VoiceTools.register("VoiceOpen")
def open_voice(mode: str, **kwargs):
    return {"action": "voice_open", "mode": mode, "status": "executed"}


@VoiceTools.register("VoiceClose")
def close_voice(**kwargs):
    return {"action": "voice_close", "status": "executed"}


@VoiceTools.register("VoiceSet")
def set_voice(volume: int, **kwargs):
    return {"action": "voice_set", "volume": volume, "status": "executed"}


class SeatTools:
    SEAT_TOOLS: Dict[str, Callable] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(func: Callable):
            cls.SEAT_TOOLS[name] = func
            return func
        return decorator

    @classmethod
    def execute(cls, tool_name: str, params: Dict) -> ToolResult:
        if tool_name not in cls.SEAT_TOOLS:
            return ToolResult(
                status=ExecuteStatus.FAILED,
                tool_name=tool_name,
                result=None,
                error=f"Unknown tool: {tool_name}"
            )
        try:
            result = cls.SEAT_TOOLS[tool_name](**params)
            return ToolResult(
                status=ExecuteStatus.SUCCESS,
                tool_name=tool_name,
                result=result
            )
        except Exception as e:
            return ToolResult(
                status=ExecuteStatus.FAILED,
                tool_name=tool_name,
                result=None,
                error=str(e)
            )


@SeatTools.register("SeatOpen")
def open_seat(feature: str, **kwargs):
    return {"action": "seat_open", "feature": feature, "status": "executed"}


@SeatTools.register("SeatClose")
def close_seat(feature: str, **kwargs):
    return {"action": "seat_close", "feature": feature, "status": "executed"}


@SeatTools.register("SeatSet")
def set_seat(position: Dict, **kwargs):
    return {"action": "seat_set", "position": position, "status": "executed"}


class ToolExecutor:
    TOOL_REGISTRY = {
        "NavigationSearchPoi": NavigationTools,
        "NavigationSetDestination": NavigationTools,
        "NavigationExit": NavigationTools,
        "NavigationSetRoutePrefer": NavigationTools,
        "WindowsOpen": WindowTools,
        "WindowsClose": WindowTools,
        "WindowsSet": WindowTools,
        "VoiceOpen": VoiceTools,
        "VoiceClose": VoiceTools,
        "VoiceSet": VoiceTools,
        "SeatOpen": SeatTools,
        "SeatClose": SeatTools,
        "SeatSet": SeatTools,
    }

    @classmethod
    def execute_intent(cls, intent_result: IntentResult) -> ToolResult:
        tool_name = intent_result.intent
        tool_class = cls.TOOL_REGISTRY.get(tool_name)
        if not tool_class:
            logger.warning(f"No tool registered for intent: {tool_name}")
            return ToolResult(
                status=ExecuteStatus.FAILED,
                tool_name=tool_name,
                result=None,
                error=f"No tool for intent: {tool_name}"
            )
        params = intent_result.metadata.get("params", {})
        return tool_class.execute(tool_name, params)

    @classmethod
    def execute(cls, intent: str, params: Optional[Dict] = None) -> ToolResult:
        tool_class = cls.TOOL_REGISTRY.get(intent)
        if not tool_class:
            return ToolResult(
                status=ExecuteStatus.FAILED,
                tool_name=intent,
                result=None,
                error=f"Unknown intent: {intent}"
            )
        return tool_class.execute(intent, params or {})

    @classmethod
    def register_tool(cls, intent: str, tool_class: type):
        cls.TOOL_REGISTRY[intent] = tool_class
        logger.info(f"Registered tool for intent: {intent}")