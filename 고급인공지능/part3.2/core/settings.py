import json
import os

CONFIG_FILE = "config.json"

def get_settings():
    """설정 파일에서 데이터를 읽어오며, 파일이 없으면 기본값을 반환합니다."""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                return {
                    "alarm_interval": int(data.get("alarm_interval", 10)) * 60, # 초 단위 변환
                    "bubble_duration": int(data.get("bubble_duration", 5)) * 1000, # ms 단위 변환
                    "news_count": int(data.get("news_count", 10)),
                    "custom_keyword": data.get("custom_keyword", "")
                }
    except Exception:
        pass
    return {"alarm_interval": 600, "bubble_duration": 5000, "news_count": 10, "custom_keyword": ""}

def save_custom_keyword(keyword):
    """사용자가 입력한 검색 키워드를 설정 파일에 저장합니다."""
    data = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
        except Exception:
            pass
    data["custom_keyword"] = keyword
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)