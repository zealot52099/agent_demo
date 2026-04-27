"""FastAPI 服务入口。"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Optional, List
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agent_system.config import settings
from agent_system.logging_config import logger
from agent.agent import Agent
from agent_system.agent.schema import IntentResult
from skills.registry import SkillRegistry
from skills.domain_classifier import DomainClassifier
from memory.conversation_memory import MemoryManager
from tools.tool_executor import ToolExecutor


app = FastAPI(
    title="Agent System API",
    description="车机语音语义理解 Agent 系统 API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_agents = {}


def get_agent(session_id: str = "default") -> Agent:
    if session_id not in _agents:
        skill_registry = SkillRegistry()
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "configs", "skills.json"
        )
        with open(config_path, "r", encoding="utf-8") as f:
            import json
            config = json.load(f)

        for domain in config["domains"]:
            skill_registry.register_domain(
                domain["name"],
                domain["description"],
                domain["skills"]
            )

        domain_classifier = DomainClassifier(config["domains"])
        _agents[session_id] = Agent(
            skill_registry=skill_registry,
            domain_classifier=domain_classifier,
            session_id=session_id,
            enable_planning=True,
            enable_execution=True
        )
        logger.info(f"Created new agent for session: {session_id}")

    return _agents[session_id]


class QueryRequest(BaseModel):
    query: str = Field(..., description="用户查询")
    session_id: str = Field(default="default", description="会话 ID")
    enable_execute: bool = Field(default=True, description="是否执行工具")
    return_full_result: bool = Field(default=False, description="是否返回完整结果")


class MultiIntentRequest(BaseModel):
    query: str = Field(..., description="多意图复合指令")
    session_id: str = Field(default="default", description="会话 ID")


class HistoryRequest(BaseModel):
    session_id: str = Field(default="default", description="会话 ID")


@app.get("/")
def root():
    return {"message": "Agent System API", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "healthy", "mock_mode": settings.mock_mode}


@app.post("/query")
def handle_query(request: QueryRequest):
    """处理单个查询"""
    try:
        agent = get_agent(request.session_id)
        result = agent.handle_query(
            query=request.query,
            enable_execute=request.enable_execute,
            return_full_result=request.return_full_result
        )
        return result
    except Exception as e:
        logger.error(f"Query handling failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/multi_intent")
def handle_multi_intent(request: MultiIntentRequest):
    """处理多意图复合指令"""
    try:
        agent = get_agent(request.session_id)
        results = agent.handle_multi_intent(request.query)
        return {"session_id": request.session_id, "results": results}
    except Exception as e:
        logger.error(f"Multi-intent handling failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history/{session_id}")
def get_history(session_id: str):
    """获取对话历史"""
    memory = MemoryManager.get_memory(session_id)
    return {
        "session_id": session_id,
        "messages": [m.to_dict() for m in memory.messages],
        "turn_count": memory.get_turn_count()
    }


@app.delete("/history/{session_id}")
def clear_history(session_id: str):
    """清除对话历史"""
    MemoryManager.clear_memory(session_id)
    if session_id in _agents:
        _agents[session_id].clear_history()
    return {"message": f"History cleared for session: {session_id}"}


@app.post("/reset/{session_id}")
def reset_session(session_id: str):
    """重置会话"""
    if session_id in _agents:
        _agents[session_id].reset_session()
    MemoryManager.clear_memory(session_id)
    return {"message": f"Session {session_id} reset"}


@app.get("/sessions")
def list_sessions():
    """列出所有会话"""
    return {"sessions": MemoryManager.list_sessions()}


@app.get("/session_info/{session_id}")
def session_info(session_id: str):
    """获取会话信息"""
    if session_id not in _agents:
        get_agent(session_id)
    return _agents[session_id].session_info


@app.get("/skills")
def list_skills():
    """列出所有技能"""
    agent = get_agent("default")
    return {
        "domains": list(agent.skill_registry.list_domains()),
        "skills": agent.skill_registry.list_skills()
    }


@app.get("/domains")
def list_domains():
    """列出所有域"""
    agent = get_agent("default")
    return {"domains": agent.domain_classifier.list_domains()}


if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on {settings.api_host}:{settings.api_port}")
    uvicorn.run(
        "agent_system.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False
    )