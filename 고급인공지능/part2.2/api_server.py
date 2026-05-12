from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import json
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 💡 설정 파일(config.json) 이름
CONFIG_FILE = "config.json"

def get_db_connection():
    conn = sqlite3.connect('news.db')
    conn.row_factory = sqlite3.Row # 결과를 MySQL처럼 딕셔너리 형태로 쓰게 해주는 마법
    return conn

# ---------------------------------------------------------
# 💡 API: 알람 주기 설정 불러오기 및 저장하기
# ---------------------------------------------------------
@app.get("/api/settings")
def get_settings():
    if not os.path.exists(CONFIG_FILE):
        return {"alarm_interval": 10} # 기본 10분
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

@app.post("/api/settings")
async def update_settings(request: Request):
    data = await request.json()
    with open(CONFIG_FILE, "w") as f:
        json.dump({"alarm_interval": int(data.get("alarm_interval", 10))}, f)
    return {"status": "success"}

# ---------------------------------------------------------
# API: 특정 카테고리의 최신 뉴스 10개 가져오기 (기존 동일)
# ---------------------------------------------------------
@app.get("/api/news/{category_code}")
def get_news(category_code: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
        SELECT id, category_code, title, url, ai_summary, created_at
        FROM news WHERE category_code = ? ORDER BY created_at DESC LIMIT 10
        """
        cursor.execute(sql, (category_code,))
        
        # SQLite의 Row 객체를 리액트가 알아들을 수 있는 순수 딕셔너리로 변환
        news_list = [dict(row) for row in cursor.fetchall()]
        
        # SQLite는 날짜를 처음부터 예쁜 문자열로 저장하므로 .strftime 변환 작업이 필요 없습니다! (삭제)
        return {"status": "success", "data": news_list}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

if __name__ == "__main__":
    print("터미널에서 아래 명령어로 서버를 켜주세요:")
    print("uvicorn api_server:app --reload")