from fastapi import APIRouter
import sqlite3
from pydantic import BaseModel
from core.database import get_db_connection
from stock_adapter import get_realtime_stock

router = APIRouter(prefix="/api")

class StockItem(BaseModel):
    name: str
    ticker: str = ""

KR_TO_EN = {
    "아마존": "Amazon", "애플": "Apple", "테슬라": "Tesla",
    "구글": "Alphabet", "알파벳": "Alphabet", "마이크로소프트": "Microsoft",
    "엔비디아": "NVIDIA", "메타": "Meta", "넷플릭스": "Netflix",
    "삼성": "Samsung", "팔란티어": "Palantir", "스타벅스": "Starbucks",
    "코카콜라": "Coca-Cola", "나이키": "Nike", "디즈니": "Disney",
}

@router.get("/stock/{ticker}")
def get_stock_price(ticker: str):
    """특정 티커의 실시간 시세를 가져옵니다."""
    return get_realtime_stock(ticker)

@router.get("/favorites")
def get_favorite_stocks():
    """DB에 등록된 관심 종목 목록을 가져옵니다."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name, ticker FROM favorite_stocks ORDER BY id ASC")
        return {"status": "success", "data": [dict(r) for r in cursor.fetchall()]}
    except:
        return {"status": "success", "data": []}
    finally:
        conn.close()

@router.post("/favorites")
def add_favorite_stock(item: StockItem):
    """새로운 관심 종목을 추가합니다. 티커가 없으면 자동으로 찾아줍니다."""
    from api_server import get_krx, get_us  # 캐시 데이터 참조
    try:
        ticker = item.ticker
        if not ticker:
            df_krx = get_krx()
            krx_match = df_krx[df_krx['Name'] == item.name]
            if not krx_match.empty:
                row = krx_match.iloc[0]
                ticker = f"{row['Code']}.KS" if row['Market'] == 'KOSPI' else f"{row['Code']}.KQ"
            else:
                en_name = KR_TO_EN.get(item.name, item.name)
                df_us = get_us()
                us_match = df_us[df_us['Name'].str.contains(en_name, case=False, na=False, regex=False)]
                if not us_match.empty:
                    ticker = us_match.iloc[0]['Symbol']
                else:
                    name_lower = item.name.lower()
                    if "비트" in name_lower or "bitcoin" in name_lower: ticker = "BTC-USD"
                    elif "이더" in name_lower or "ethereum" in name_lower: ticker = "ETH-USD"
                    else: return {"status": "error", "message": f"'{item.name}' 종목을 찾지 못했습니다."}

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO favorite_stocks (name, ticker) VALUES (?, ?)", (item.name, ticker))
        conn.commit()
        return {"status": "success"}
    except sqlite3.IntegrityError:
        return {"status": "error", "message": f"[{item.name}] 이미 등록된 관심종목입니다!"}
    except Exception as e:
        return {"status": "error", "message": f"오류 발생: {e}"}
    finally:
        if 'conn' in locals(): conn.close()

@router.delete("/favorites/{id}")
def delete_favorite_stock(id: int):
    """관심 종목을 삭제합니다."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM favorite_stocks WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"status": "success"}

@router.get("/search_stock")
def search_stock(name: str):
    """이름으로 주식 종목을 실시간 검색하여 자동완성 목록을 제공합니다."""
    # api_server에 캐싱된 주식 데이터(한국/미국)를 가져옵니다.
    from api_server import get_krx, get_us 
    
    if not name or len(name) < 1:
        return {"status": "success", "data": []}
        
    try:
        df_krx = get_krx()
        df_us = get_us()
        
        # 1. 한국 주식 및 미국 주식에서 이름이 포함된 종목 검색
        krx_match = df_krx[df_krx['Name'].str.contains(name, case=False, na=False)]
        us_match = df_us[df_us['Name'].str.contains(name, case=False, na=False)]
        
        results = []
        
        # 한국 주식 결과 추가 (최대 5개만)
        for _, row in krx_match.head(5).iterrows():
            ticker = f"{row['Code']}.KS" if row['Market'] == 'KOSPI' else f"{row['Code']}.KQ"
            results.append({"name": row['Name'], "ticker": ticker})
            
        # 미국 주식 결과 추가 (최대 5개만)
        for _, row in us_match.head(5).iterrows():
            results.append({"name": row['Name'], "ticker": row['Symbol']})
            
        return {"status": "success", "data": results}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}