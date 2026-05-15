from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import json
import os
from pydantic import BaseModel
from stock_adapter import get_realtime_stock

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CONFIG_FILE = "config.json"

# ---------------------------------------------------------
# 💡 데이터 규칙 정의
# ---------------------------------------------------------
class StockItem(BaseModel):
    name: str

class ScheduleItem(BaseModel):
    date: str
    content: str

class ClipboardItem(BaseModel):
    type: str
    content: str

def get_db_connection():
    conn = sqlite3.connect('news.db')
    conn.row_factory = sqlite3.Row 
    return conn

# ---------------------------------------------------------
# 💡 주식 목록 캐시 (pkl 파일로 저장 → 서버 재시작해도 즉시 로드)
# ---------------------------------------------------------
import pickle
import datetime as _dt

CACHE_FILE = "stock_cache.pkl"
CACHE_MAX_AGE_DAYS = 1  # 하루에 한 번 자동 갱신

_df_krx = None
_df_us = None

def _load_cache():
    """pkl 파일에서 캐시 불러오기. 오래됐으면 None 반환."""
    global _df_krx, _df_us
    if not os.path.exists(CACHE_FILE):
        return False
    try:
        with open(CACHE_FILE, "rb") as f:
            cache = pickle.load(f)
        saved_at = cache.get("saved_at")
        age = (_dt.datetime.now() - saved_at).days
        if age >= CACHE_MAX_AGE_DAYS:
            print(f"⏰ 주식 캐시가 {age}일 지났습니다. 새로 다운로드합니다.")
            return False
        _df_krx = cache["krx"]
        _df_us  = cache["us"]
        print(f"✅ 주식 캐시 로드 완료 (KRX {len(_df_krx)}개 / US {len(_df_us)}개)")
        return True
    except Exception as e:
        print(f"⚠️ 캐시 파일 오류: {e} → 새로 다운로드합니다.")
        return False

def _download_and_save():
    """KRX/US 목록 새로 다운받아서 pkl로 저장."""
    global _df_krx, _df_us
    import FinanceDataReader as fdr
    print("📡 KRX 종목 목록 다운로드 중...")
    _df_krx = fdr.StockListing('KRX')
    print(f"   → KRX {len(_df_krx)}개 완료")
    print("📡 US 종목 목록 다운로드 중...")
    _df_us = fdr.StockListing('US')
    print(f"   → US {len(_df_us)}개 완료")
    with open(CACHE_FILE, "wb") as f:
        pickle.dump({"krx": _df_krx, "us": _df_us, "saved_at": _dt.datetime.now()}, f)
    print(f"💾 주식 목록 저장 완료 → {CACHE_FILE}")

def get_krx():
    if _df_krx is None:
        _download_and_save()
    return _df_krx

def get_us():
    if _df_us is None:
        _download_and_save()
    return _df_us

# ---------------------------------------------------------
# 💡 서버 시작 시 DB 테이블 세팅 + 주식 목록 캐시 로드
# ---------------------------------------------------------
@app.on_event("startup")
def startup_event():
    # 캐시 파일 있으면 즉시 로드, 없거나 오래됐으면 백그라운드에서 새로 다운로드
    if not _load_cache():
        import threading
        threading.Thread(target=_download_and_save, daemon=True).start()
        print("⏳ 주식 목록 백그라운드 다운로드 시작 (첫 검색은 잠시 후 가능)")

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS schedule (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        content TEXT NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clipboard (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS favorite_stocks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        ticker TEXT NOT NULL UNIQUE
    )
    ''')
    
    # 💡 처음 켰을 때 비어있으면 기본 종목 3개 꽂아주기
    cursor.execute("SELECT COUNT(*) FROM favorite_stocks")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO favorite_stocks (name, ticker) VALUES ('애플', 'AAPL')")
        cursor.execute("INSERT INTO favorite_stocks (name, ticker) VALUES ('테슬라', 'TSLA')")
        cursor.execute("INSERT INTO favorite_stocks (name, ticker) VALUES ('삼성전자', '005930.KS')")
    
    conn.commit()
    conn.close()

# ---------------------------------------------------------
# 📅 [달력 API]
# ---------------------------------------------------------
@app.get("/api/schedule/{date}")
def get_schedule(date: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, content FROM schedule WHERE date = ? ORDER BY id ASC", (date,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"status": "success", "data": rows}

@app.post("/api/schedule")
def add_schedule(item: ScheduleItem):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO schedule (date, content) VALUES (?, ?)", (item.date, item.content))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.delete("/api/schedule/{id}")
def delete_schedule(id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM schedule WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"status": "success"}

# ---------------------------------------------------------
# ⚙️ [설정 API]
# ---------------------------------------------------------
@app.get("/api/settings")
def get_settings_api():
    if not os.path.exists(CONFIG_FILE):
        return {"alarm_interval": 10, "enabled_categories": ["01", "02", "03", "04", "05", "06", "07", "08"], "bubble_duration": 5, "news_count": 10}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

@app.post("/api/settings")
async def update_settings(request: Request):
    data = await request.json()
    current_settings = get_settings_api()
    current_settings.update(data)
    with open(CONFIG_FILE, "w") as f:
        json.dump(current_settings, f)
    return {"status": "success"}

# ---------------------------------------------------------
# 📰 [뉴스 API] 
# ---------------------------------------------------------
@app.get("/api/news/{category_code}")
def get_news(category_code: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = "SELECT id, category_code, title, url, ai_summary, created_at FROM news WHERE category_code = ? ORDER BY created_at DESC LIMIT 10"
        cursor.execute(sql, (category_code,))
        news_list = [dict(row) for row in cursor.fetchall()]
        return {"status": "success", "data": news_list}
    except Exception as e: return {"status": "error", "message": str(e)}
    finally: conn.close()

@app.get("/api/search")
def search_news(keyword: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = "SELECT id, category_code, title, url, ai_summary, created_at FROM news WHERE title LIKE ? OR ai_summary LIKE ? ORDER BY created_at DESC LIMIT 20"
        search_term = f"%{keyword}%"
        cursor.execute(sql, (search_term, search_term))
        news_list = [dict(row) for row in cursor.fetchall()]
        return {"status": "success", "data": news_list}
    except Exception as e: return {"status": "error", "message": str(e)}
    finally: conn.close()

# ---------------------------------------------------------
# 📋 [클립보드 API]
# ---------------------------------------------------------
@app.get("/api/clipboard")
def get_clipboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, type, content, created_at FROM clipboard ORDER BY created_at DESC LIMIT 20")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"status": "success", "data": rows}

@app.post("/api/clipboard")
def add_clipboard(item: ClipboardItem):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clipboard (type, content) VALUES (?, ?)", (item.type, item.content))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.delete("/api/clipboard/{id}")
def delete_clipboard(id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clipboard WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"status": "success"}

# ---------------------------------------------------------
# 📈 [주식 API]
# ---------------------------------------------------------
@app.get("/api/stock/{ticker}")
def get_stock(ticker: str):
    return get_realtime_stock(ticker)

@app.get("/api/favorites")
def get_favorite_stocks():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name, ticker FROM favorite_stocks ORDER BY id ASC")
        rows = [dict(r) for r in cursor.fetchall()]
        return {"status": "success", "data": rows}
    except Exception:
        return {"status": "success", "data": []}
    finally:
        conn.close()

# 💡 한글 이름 → 영문 매핑 테이블 (자주 쓰는 미국주식)
KR_TO_EN = {
    "아마존": "Amazon", "애플": "Apple", "테슬라": "Tesla",
    "구글": "Alphabet", "알파벳": "Alphabet", "마이크로소프트": "Microsoft",
    "엔비디아": "NVIDIA", "메타": "Meta", "넷플릭스": "Netflix",
    "삼성": "Samsung", "팔란티어": "Palantir", "스타벅스": "Starbucks",
    "코카콜라": "Coca-Cola", "나이키": "Nike", "디즈니": "Disney",
}

@app.get("/api/search_stock")
def search_stock(name: str):
    """입력한 이름으로 종목 추천 목록 반환 (캐시 사용 → 빠름)"""
    try:
        results = []

        # 1. KRX에서 한글 이름으로 검색 (캐시 사용)
        df_krx = get_krx()
        krx_matches = df_krx[df_krx['Name'].str.contains(name, case=False, na=False)].head(5)
        for _, row in krx_matches.iterrows():
            code = row['Code']
            market = row['Market']
            ticker = f"{code}.KS" if market == 'KOSPI' else f"{code}.KQ"
            results.append({"name": row['Name'], "ticker": ticker})

        # 2. 미국 주식: 한글 → 영문 변환 후 검색 (캐시 사용)
        en_name = KR_TO_EN.get(name, name)
        df_us = get_us()
        us_matches = df_us[df_us['Name'].str.contains(en_name, case=False, na=False)].head(5)
        for _, row in us_matches.iterrows():
            results.append({"name": row['Name'], "ticker": row['Symbol']})

        return {"status": "success", "data": results[:8]}
    except Exception as e:
        return {"status": "error", "data": [], "message": str(e)}

@app.post("/api/favorites")
def add_favorite_stock(item: StockItem):
    try:
        # 캐시 사용 → 빠름
        df_krx = get_krx()
        krx_match = df_krx[df_krx['Name'] == item.name]
        
        ticker = ""
        if not krx_match.empty:
            row = krx_match.iloc[0]
            code = row['Code']
            market = row['Market']
            ticker = f"{code}.KS" if market == 'KOSPI' else f"{code}.KQ"
        else:
            en_name = KR_TO_EN.get(item.name, item.name)
            df_us = get_us()
            us_match = df_us[df_us['Name'].str.contains(en_name, case=False, na=False)]
            
            if not us_match.empty:
                ticker = us_match.iloc[0]['Symbol']
            else:
                if "비트" in item.name or "bitcoin" in item.name.lower():
                    ticker = "BTC-USD"
                elif "이더" in item.name or "ethereum" in item.name.lower():
                    ticker = "ETH-USD"
                else:
                    return {"status": "error", "message": f"'{item.name}' 종목을 찾지 못했습니다."}

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO favorite_stocks (name, ticker) VALUES (?, ?)", (item.name, ticker))
        conn.commit()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": "이미 등록된 종목이거나 오류가 발생했습니다."}
    finally:
        if 'conn' in locals(): conn.close()

@app.delete("/api/favorites/{id}")
def delete_favorite_stock(id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM favorite_stocks WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"status": "success"}

if __name__ == "__main__":
    print("터미널에서 아래 명령어로 서버를 켜주세요:")
    print("uvicorn api_server:app --reload")