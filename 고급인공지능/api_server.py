from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pymysql
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
    return pymysql.connect(
        host='localhost', user='root', password='rla1dbs2', 
        db='news_db', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
    )

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
            FROM news WHERE category_code = %s ORDER BY created_at DESC LIMIT 10
        """
        cursor.execute(sql, (category_code,))
        news_list = cursor.fetchall()
        for news in news_list:
            if news['created_at']:
                news['created_at'] = news['created_at'].strftime("%Y-%m-%d %H:%M")
        return {"status": "success", "data": news_list}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

if __name__ == "__main__":
    print("터미널에서 아래 명령어로 서버를 켜주세요:")
    print("uvicorn api_server:app --reload")