from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import date
from pydantic import BaseModel
import json
import os
from pathlib import Path

router = APIRouter(
    prefix="/api/meal-count",
    tags=["meal-count"],
    responses={404: {"description": "Not found"}}
)

# 데이터를 저장할 경로
DATA_DIR = Path("data")
DATA_FILE = DATA_DIR / "meal_counts.json"

# 데이터 디렉토리 생성
DATA_DIR.mkdir(exist_ok=True)

# 식사 인원 데이터 모델
class MealCountData(BaseModel):
    date: date
    count: int

# 데이터 불러오기
def load_data() -> dict:
    if not DATA_FILE.exists():
        return {}
    
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

# 데이터 저장하기
def save_data(data: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, default=str)

@router.post("/save")
async def save_meal_count(meal_data: MealCountData):
    """식사 인원 정보 저장"""
    data = load_data()
    date_str = str(meal_data.date)
    
    data[date_str] = meal_data.count
    save_data(data)
    
    return {"success": True, "message": f"{date_str}에 {meal_data.count}명의 식사 인원이 저장되었습니다."}

@router.get("/all")
async def get_all_meal_counts():
    """모든 식사 인원 정보 조회"""
    data = load_data()
    return data

@router.get("/{date_str}")
async def get_meal_count(date_str: str):
    """특정 날짜의 식사 인원 정보 조회"""
    data = load_data()
    
    if date_str not in data:
        raise HTTPException(status_code=404, detail=f"{date_str}에 대한 식사 인원 정보가 없습니다.")
    
    return {"date": date_str, "count": data[date_str]}

@router.put("/{date_str}")
async def update_meal_count(date_str: str, meal_data: MealCountData):
    """특정 날짜의 식사 인원 정보 수정"""
    data = load_data()
    
    if date_str not in data:
        raise HTTPException(status_code=404, detail=f"{date_str}에 대한 식사 인원 정보가 없습니다.")
    
    data[date_str] = meal_data.count
    save_data(data)
    
    return {"success": True, "message": f"{date_str}에 {meal_data.count}명의 식사 인원이 수정되었습니다."}

@router.delete("/{date_str}")
async def delete_meal_count(date_str: str):
    """특정 날짜의 식사 인원 정보 삭제"""
    data = load_data()
    
    if date_str not in data:
        raise HTTPException(status_code=404, detail=f"{date_str}에 대한 식사 인원 정보가 없습니다.")
    
    del data[date_str]
    save_data(data)
    
    return {"success": True, "message": f"{date_str}의 식사 인원 정보가 삭제되었습니다."} 