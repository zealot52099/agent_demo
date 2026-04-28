"""Agent 核心 - 整合 Memory、Planner、ToolExecutor。"""
from typing import List, Dict, Optional, Any

from agent.schema import IntentResult
from agent.inference import run_inference, run_inference_with_fallback
from skills.registry import SkillRegistry
from skills.domain_classifier import DomainClassifier
from memory.conversation_memory import ConversationMemory, MemoryManager
from tools.tool_executor import ToolExecutor, ToolResult, ExecuteStatus
from planner.task_planner import Planner, Task, TaskStatus
from agent_system.logging_config import logger


class AgentError(Exception):
    pass


class DomainClassificationError(AgentError):
    pass


class IntentParsingError(AgentError):
    pass


class ToolExecutionError(AgentError):
    pass


class Agent:
    def __init__(
        self,
        skill_registry: SkillRegistry,
        domain_classifier: Optional[DomainClassifier] = None,
        session_id: Optional[str] = None,
        enable_planning: bool = True,
        enable_execution: bool = True
    ):
        self.skill_registry = skill_registry
        self.domain_classifier = domain_classifier
        self.session_id = session_id or "default"
        self.memory = MemoryManager.get_memory(self.session_id)
        self.planner = Planner() if enable_planning else None
        self.enable_execution = enable_execution
        self._execution_history: List[Dict] = []

    def handle_query(
        self,
        query: str,
        enable_execute: Optional[bool] = None,
        return_full_result: bool = False
    ) -> Dict[str, Any]:
        """
        处理用户查询的完整流程

        Args:
            query: 用户输入
            enable_execute: 是否执行工具（默认使用 self.enable_execution）
            return_full_result: 是否返回完整结果（包含中间状态）

        Returns:
            如果 return_full_result=False，返回 str（最终响应）
            如果 return_full_result=True，返回完整结果字典
        """
        should_execute = enable_execute if enable_execute is not None else self.enable_execution

        logger.info(f"Handling query: {query[:50]}...")
        self.memory.add_user_message(query)

        try:
            intent_result, raw_output = self._single_stage_inference(query)
            logger.info(f"Single stage - Raw output: {raw_output}")
            logger.info(f"Parsed intent: {intent_result.intent}, domain: {intent_result.domain}")

            if should_execute:
                tool_result = self._execute_intent(intent_result)
                logger.info(f"Tool execution: {tool_result.status.value}")

            response = self._format_response(intent_result, raw_output)
            self.memory.add_assistant_message(response)

            if return_full_result:
                return {
                    "response": response,
                    "domain": intent_result.domain,
                    "intent": intent_result.intent,
                    "asr_text": intent_result.asr_text,
                    "confidence": intent_result.confidence,
                    "tool_executed": should_execute,
                    "tool_result": tool_result.to_dict() if should_execute else None,
                    "history_turns": self.memory.get_turn_count()
                }
            return response

        except Exception as e:
            error_msg = f"处理查询时出错: {str(e)}"
            logger.error(error_msg)
            self.memory.add_assistant_message(error_msg)
            return error_msg if not return_full_result else {"error": error_msg}

    def _single_stage_inference(self, query: str):
        """单阶段推理：模型自主决策是否需要域知识"""
        history = self.memory.get_history_for_inference()
        prompt = self.domain_classifier.get_single_stage_prompt(query, history)
        logger.info(f"history for single stage: {history}")

        raw_output = run_inference_with_fallback(prompt)

        intent = self.domain_classifier.match_single_intent(raw_output)
        if intent:
            return IntentResult(
                asr_text=query,
                intent=intent,
                confidence=1.0,
                domain=None,
                raw_output=raw_output
            ), raw_output

        need_domain = self.domain_classifier.match_need_domain(raw_output)
        if need_domain:
            logger.info(f"Model requests domain knowledge: {need_domain}")
            prompt2 = self.domain_classifier.get_stage2_prompt(need_domain, query, history)
            raw_output2 = run_inference_with_fallback(prompt2)

            intent = self.domain_classifier.match_intent_from_domain(raw_output2, need_domain)
            if intent:
                return IntentResult(
                    asr_text=query,
                    intent=intent,
                    confidence=1.0,
                    domain=need_domain,
                    raw_output=raw_output2
                ), raw_output2

        return IntentResult(
            asr_text=query,
            intent="NoiseAction",
            confidence=0.0,
            domain=None,
            raw_output=raw_output
        ), raw_output

    def _stage1_domain_classification(self, query: str) -> Dict:
        """第一阶段：域分类"""
        if not self.domain_classifier:
            return {"domain": "Unknown", "raw_output": "No domain classifier"}

        
        history = self.memory.get_history_for_inference()
        prompt = self.domain_classifier.get_stage1_prompt(query, history)
        logger.info(f"history for stage 1: {history}")
        try:
            # raw_output = run_inference_with_fallback(prompt, history)
            raw_output = run_inference_with_fallback(prompt)
            logger.info(f"Stage 1 - Raw output: {raw_output}")
        except Exception as e:
            logger.error(f"Stage 1 inference failed: {e}")
            raw_output = ""

        domain_name = self.domain_classifier.match_domain(raw_output)
        return {"domain": domain_name, "raw_output": raw_output}

    def _stage2_intent_matching(self, query: str, domain_name: str) -> Dict:
        """第二阶段：域内意图精确匹配"""
        if not self.domain_classifier:
            return {"raw_output": "No domain classifier"}

        # prompt = self.domain_classifier.get_stage2_prompt(domain_name, query)
        history = self.memory.get_history_for_inference()
        prompt = self.domain_classifier.get_stage2_prompt(domain_name, query, history)
        logger.info(f"history for stage 2: {history}")
        try:
            # raw_output = run_inference_with_fallback(prompt, history)
            raw_output = run_inference_with_fallback(prompt)
        except Exception as e:
            logger.error(f"Stage 2 inference failed: {e}")
            raw_output = ""

        return {"raw_output": raw_output}

    def _parse_intent_result(self, raw_output: str, domain: Optional[str]) -> IntentResult:
        """解析 IntentResult，使用 schema 校验"""
        try:
            return IntentResult.parse_pipe_format(raw_output, domain)
        except Exception as e:
            logger.warning(f"Intent parse failed, using fallback: {e}")
            return IntentResult(
                asr_text=raw_output,
                intent="NoiseAction",
                confidence=0.0,
                domain=domain,
                raw_output=raw_output
            )

    def _execute_intent(self, intent_result: IntentResult) -> ToolResult:
        """执行意图对应的工具"""
        try:
            return ToolExecutor.execute_intent(intent_result)
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return ToolResult(
                status=ExecuteStatus.FAILED,
                tool_name=intent_result.intent,
                result=None,
                error=str(e)
            )

    def _format_response(self, intent_result: IntentResult, raw_output: str) -> str:
        """格式化最终响应"""
        if intent_result.intent == "NoiseAction":
            return f"格式解析失败或无法理解。原始输出: {raw_output}"

        # return f"已识别您的意图：{intent_result.intent}，ASR结果：{intent_result.asr_text}"
        return f"已识别您的意图：{intent_result.intent}"

    def handle_multi_intent(self, query: str) -> List[Dict[str, Any]]:
        """处理多意图复合指令"""
        if not self.planner:
            return [self.handle_query(query, return_full_result=True)]

        sub_intents = self.planner.parse_multi_intent(query)
        results = []

        for i, sub_intent in enumerate(sub_intents):
            logger.info(f"Processing sub-intent {i+1}/{len(sub_intents)}: {sub_intent.asr_text}")
            result = self.handle_query(sub_intent.asr_text, return_full_result=True)
            results.append(result)

        return results

    def get_history(self) -> List[Dict]:
        """获取对话历史"""
        return self.memory.get_history_for_inference()

    def clear_history(self):
        """清除对话历史"""
        self.memory.clear()
        logger.info("History cleared")

    def get_execution_history(self) -> List[Dict]:
        """获取工具执行历史"""
        return self._execution_history.copy()

    def reset_session(self):
        """重置会话（清除记忆但保留配置）"""
        MemoryManager.clear_memory(self.session_id)
        self.memory = MemoryManager.get_memory(self.session_id)
        self._execution_history.clear()
        logger.info(f"Session {self.session_id} reset")

    @property
    def session_info(self) -> Dict:
        return {
            "session_id": self.session_id,
            "turn_count": self.memory.get_turn_count(),
            "history_length": len(self.memory.messages),
            "tool_executions": len(self._execution_history)
        }