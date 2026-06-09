from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import pandas as pd
import pickle
import datetime as _dt
import threading

# core 및 api 라우터 임포트
from core.database import init_db
from api.news_api import router as news_router
from api.stock_api import router as stock_router
from api.schedule_api import router as schedule_router
from api.settings_api import router as settings_router
app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 연결
app.include_router(news_router)
app.include_router(stock_router)
app.include_router(schedule_router)
app.include_router(settings_router)
# ---------------------------------------------------------
# 📈 주식 종목 데이터 캐싱 및 다운로드 로직
# ---------------------------------------------------------
CACHE_FILE = "stock_cache.pkl"
CACHE_MAX_AGE_DAYS = 1

_df_krx = None
_df_us = None

def _load_cache():
    global _df_krx, _df_us
    if not os.path.exists(CACHE_FILE): return False
    try:
        with open(CACHE_FILE, "rb") as f:
            cache = pickle.load(f)
        saved_at = cache.get("saved_at")
        if (_dt.datetime.now() - saved_at).days >= CACHE_MAX_AGE_DAYS: return False
        _df_krx = cache["krx"]
        _df_us  = cache["us"]
        print(f"✅ 주식 캐시 로드 완료 (KRX {len(_df_krx)}개 / US {len(_df_us)}개)")
        return True
    except: return False

def _download_and_save():
    global _df_krx, _df_us
    import FinanceDataReader as fdr
    print("📡 KRX 종목 목록 다운로드 중...")
    _df_krx = fdr.StockListing('KRX')
    print("📡 US 종목 목록 다운로드 중...")
    df_nasdaq = fdr.StockListing('NASDAQ')
    df_nyse   = fdr.StockListing('NYSE')
    df_amex   = fdr.StockListing('AMEX')
    _df_us = pd.concat([df_nasdaq, df_nyse, df_amex], ignore_index=True)
    with open(CACHE_FILE, "wb") as f:
        pickle.dump({"krx": _df_krx, "us": _df_us, "saved_at": _dt.datetime.now()}, f)
    print("✅ 주식 데이터 업데이트 완료")

def get_krx():
    global _df_krx
    if _df_krx is None:
        if not _load_cache(): _download_and_save()
    return _df_krx

def get_us():
    global _df_us
    if _df_us is None:
        if not _load_cache(): _download_and_save()
    return _df_us

# ---------------------------------------------------------
# 🚀 서버 시작 및 종료 이벤트
# ---------------------------------------------------------
@app.on_event("startup")
def startup_event():
    # DB 테이블 초기화 (core/database.py)
    init_db()
    
    # 주식 데이터 캐시 로드 또는 다운로드
    if not _load_cache():
        threading.Thread(target=_download_and_save, daemon=True).start()

# ---------------------------------------------------------
# 📂 정적 파일 서빙 (React 빌드 결과물)
# ---------------------------------------------------------
if os.path.exists("news-app/dist"):
    app.mount("/", StaticFiles(directory="news-app/dist", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    print("🚀 자비스 API 서버 가동 중 (Port: 8000)")
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)