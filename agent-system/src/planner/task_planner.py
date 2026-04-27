"""意图规划器 - 任务拆解与反思。"""
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

from agent_system.logging_config import logger
from agent_system.agent.schema import IntentResult


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    task_id: str
    intent: str
    params: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "intent": self.intent,
            "params": self.params,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "dependencies": self.dependencies
        }


class Planner:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}

    def create_task(self, intent: str, params: Optional[Dict] = None, dependencies: Optional[List[str]] = None) -> Task:
        import uuid
        task_id = str(uuid.uuid4())[:8]
        task = Task(
            task_id=task_id,
            intent=intent,
            params=params or {},
            dependencies=dependencies or []
        )
        self.tasks[task_id] = task
        logger.info(f"Created task {task_id}: {intent}")
        return task

    def parse_multi_intent(self, query: str) -> List[IntentResult]:
        """将复合指令拆分为多个独立意图"""
        indicators = ["然后", "并且", "同时", "再", "和", "及"]
        parts = [query]
        for indicator in indicators:
            new_parts = []
            for part in parts:
                new_parts.extend(part.split(indicator))
            if len(new_parts) > 1:
                parts = new_parts
                break
        results = []
        for i, part in enumerate(parts):
            part = part.strip()
            if part:
                results.append(IntentResult(
                    asr_text=part,
                    intent=f"Task_{i+1}",
                    confidence=1.0
                ))
        logger.debug(f"Parsed {len(results)} sub-intents from multi-intent query")
        return results

    def plan(self, intent_results: List[IntentResult]) -> List[Task]:
        """根据意图结果生成执行计划"""
        tasks = []
        for i, result in enumerate(intent_results):
            deps = []
            if i > 0 and self._requires_previous(result.intent):
                deps.append(tasks[i-1].task_id)
            task = self.create_task(
                intent=result.intent,
                params={"asr": result.asr_text, "domain": result.domain},
                dependencies=deps
            )
            tasks.append(task)
        logger.info(f"Planned {len(tasks)} tasks")
        return tasks

    def _requires_previous(self, intent: str) -> bool:
        """判断意图是否依赖前一个任务完成"""
        sequential_keywords = ["导航到", "设置目的地", "播放"]
        return any(kw in intent for kw in sequential_keywords)

    def validate_plan(self, tasks: List[Task]) -> bool:
        """验证执行计划的合理性"""
        if not tasks:
            return False
        for task in tasks:
            if task.status == TaskStatus.FAILED:
                return False
        return True

    def get_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)

    def update_task_status(self, task_id: str, status: TaskStatus, result: Any = None, error: Optional[str] = None):
        if task_id in self.tasks:
            self.tasks[task_id].status = status
            if result is not None:
                self.tasks[task_id].result = result
            if error:
                self.tasks[task_id].error = error
            logger.info(f"Task {task_id} status updated to {status.value}")