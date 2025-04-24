from pydantic import BaseModel
from typing import List, Optional


class MealCountResult(BaseModel):
    """식사 인원 계산 결과 모델"""
    count: int
    included_people: List[str]
    excluded_people: List[str]
    default_count: int


class EmailDetails(BaseModel):
    """이메일 전송 세부 정보 모델"""
    to: str
    subject: str
    count: int 