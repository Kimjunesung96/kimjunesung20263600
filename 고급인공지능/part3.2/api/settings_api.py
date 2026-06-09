from fastapi import APIRouter
from pydantic import BaseModel
import json
import os

router = APIRouter(prefix="/api")
CONFIG_FILE = "config.json"

# 프론트엔드에서 넘어오는 설정 데이터의 형식 정의
class SettingsModel(BaseModel):
    alarm_interval: int = None
    enabled_categories: list = None
    bubble_duration: int = None
    news_count: int = None

@router.get("/settings")
def get_settings():
    """React 화면이 켜질 때 기존 설정을 불러옵니다."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except Exception:
            pass
    return {}

@router.post("/settings")
def save_settings(settings: SettingsModel):
    """React 화면에서 변경한 설정을 config.json에 저장합니다."""
    data = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            pass
            
    # 새로 들어온 값들만 기존 데이터에 덮어쓰기
    update_data = settings.dict(exclude_none=True)
    for key, value in update_data.items():
        data[key] = value
            
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        
    return {"status": "success", "message": "설정이 저장되었습니다."}