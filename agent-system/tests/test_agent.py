"""Agent 核心模块测试。"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agent_system.agent.schema import IntentResult
from memory.conversation_memory import ConversationMemory, MemoryManager
from tools.tool_executor import ToolExecutor, ExecuteStatus
from planner.task_planner import Planner, TaskStatus


class TestIntentResult:
    def test_parse_pipe_format_basic(self):
        raw = "导航到加油站|NavigationSearchPoi"
        result = IntentResult.parse_pipe_format(raw, "导航控制域")
        assert result.asr_text == "导航到加油站"
        assert result.intent == "NavigationSearchPoi"
        assert result.domain == "导航控制域"

    def test_parse_pipe_format_with_tags(self):
        raw = "<answer>打开空调|NavigationSetRoutePrefer</answer>"
        result = IntentResult.parse_pipe_format(raw, "导航控制域")
        assert result.intent == "NavigationSetRoutePrefer"
        assert result.asr_text == "打开空调"

    def test_parse_pipe_format_fallback(self):
        raw = "无法解析的内容"
        result = IntentResult.parse_pipe_format(raw, "导航控制域")
        assert result.intent == "NoiseAction"
        assert result.confidence == 0.0

    def test_invalid_intent_format(self):
        raw = "text|123-invalid"
        result = IntentResult.parse_pipe_format(raw, "导航控制域")
        assert result.intent == "NoiseAction"


class TestConversationMemory:
    def test_add_messages(self):
        memory = ConversationMemory(max_turns=3)
        memory.add_user_message("打开空调")
        memory.add_assistant_message("已执行")

        assert len(memory.messages) == 2
        assert memory.get_turn_count() == 1

    def test_history_trim(self):
        memory = ConversationMemory(max_turns=2)
        for i in range(10):
            memory.add_user_message(f"query {i}")
            memory.add_assistant_message(f"response {i}")

        assert len(memory.messages) <= 4

    def test_get_history_for_inference(self):
        memory = ConversationMemory()
        memory.add_user_message("test")
        memory.add_assistant_message("result")

        history = memory.get_history_for_inference()
        assert len(history) == 2
        assert history[0]["role"] == "user"

    def test_get_last_user_message(self):
        memory = ConversationMemory()
        memory.add_user_message("first")
        memory.add_assistant_message("middle")
        memory.add_user_message("last")

        assert memory.get_last_user_message() == "last"


class TestMemoryManager:
    def test_get_memory(self):
        MemoryManager._instances.clear()
        mem1 = MemoryManager.get_memory("session1")
        mem2 = MemoryManager.get_memory("session1")
        mem3 = MemoryManager.get_memory("session2")

        assert mem1 is mem2
        assert mem1 is not mem3

    def test_clear_memory(self):
        MemoryManager._instances.clear()
        mem = MemoryManager.get_memory("test_session")
        mem.add_user_message("test")

        MemoryManager.clear_memory("test_session")
        assert "test_session" not in MemoryManager._instances


class TestToolExecutor:
    def test_execute_navigation_tool(self):
        intent = IntentResult(
            asr_text="导航到加油站",
            intent="NavigationSearchPoi",
            confidence=0.9,
            domain="导航控制域",
            metadata={"params": {"poi_name": "加油站"}}
        )

        result = ToolExecutor.execute_intent(intent)
        assert result.status == ExecuteStatus.SUCCESS
        assert result.tool_name == "NavigationSearchPoi"

    def test_execute_unknown_tool(self):
        intent = IntentResult(
            asr_text="未知指令",
            intent="UnknownTool",
            confidence=0.1
        )

        result = ToolExecutor.execute_intent(intent)
        assert result.status == ExecuteStatus.FAILED

    def test_direct_execute(self):
        result = ToolExecutor.execute("WindowsOpen", {"window_type": "all"})
        assert result.status == ExecuteStatus.SUCCESS


class TestPlanner:
    def test_create_task(self):
        planner = Planner()
        task = planner.create_task("NavigationSearchPoi", {"poi": "加油站"})

        assert task.task_id is not None
        assert task.intent == "NavigationSearchPoi"
        assert task.params["poi"] == "加油站"

    def test_parse_multi_intent(self):
        planner = Planner()
        results = planner.parse_multi_intent("打开空调然后导航到加油站")

        assert len(results) >= 2

    def test_plan_intents(self):
        planner = Planner()
        intent_results = [
            IntentResult(asr_text="打开空调", intent="SeatOpen", confidence=0.9),
            IntentResult(asr_text="导航到加油站", intent="NavigationSearchPoi", confidence=0.9)
        ]

        tasks = planner.plan(intent_results)
        assert len(tasks) == 2
        assert tasks[0].status == TaskStatus.PENDING


class TestAgent:
    def test_agent_initialization(self):
        from agent.agent import Agent
        from skills.registry import SkillRegistry
        from skills.domain_classifier import DomainClassifier

        registry = SkillRegistry()
        classifier = DomainClassifier([{
            "name": "测试域",
            "description": "测试用域",
            "skills": [{"name": "TestAction", "description": "测试意图"}]
        }])

        agent = Agent(registry, classifier, session_id="test")
        assert agent.session_id == "test"
        assert agent.memory is not None

    def test_agent_handle_query(self):
        from agent.agent import Agent
        from skills.registry import SkillRegistry
        from skills.domain_classifier import DomainClassifier

        registry = SkillRegistry()
        classifier = DomainClassifier([{
            "name": "导航控制域",
            "description": "导航相关",
            "skills": [{"name": "NavigationSearchPoi", "description": "搜索POI"}]
        }])

        agent = Agent(registry, classifier, session_id="test")
        agent.enable_execution = False

        result = agent.handle_query("导航到加油站", enable_execute=False)
        assert isinstance(result, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])