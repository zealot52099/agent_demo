"""API 路由定义。"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.get("/domains")
def list_domains():
    return {"domains": []}


@router.get("/skills")
def list_skills():
    return {"skills": []}