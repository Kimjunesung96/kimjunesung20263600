# ==========================================
# 💡 주식 데이터 어댑터 (수도관 교체용 파일)
# ==========================================
# 나중에 유료 API(Polygon, 키움증권 등)로 갈아끼울 때는 
# 이 파일 안의 내용만 유료 API 호출 방식으로 싹 바꾸면 됩니다!
# (단, 맨 아래 반환하는 return 딕셔너리 모양만 똑같이 유지하세요)

import yfinance as yf

def get_realtime_stock(ticker):
    try:
        # 1. 야후 파이낸스에서 종목 검색
        stock = yf.Ticker(ticker)
        
        # 2. 최근 5일치 데이터 가져오기 (주말/휴일 고려)
        hist = stock.history(period="5d")
        
        if len(hist) < 2:
            return {"status": "error", "message": "데이터를 불러올 수 없습니다."}

        # 어제 종가와 오늘 현재가(또는 오늘 종가) 추출
        yesterday_close = hist['Close'].iloc[-2]
        current_price = hist['Close'].iloc[-1]
        
        # 변동 금액 및 변동률 계산
        diff = current_price - yesterday_close
        diff_percent = (diff / yesterday_close) * 100

        # 3. 💡 [핵심] 어떤 API를 쓰든 무조건 이 '통일된 모양'으로 반환하도록 약속!
        return {
            "status": "success",
            "price": round(current_price, 2),        # 현재가
            "diff": round(diff, 2),                  # 변동 금액 (어제 대비)
            "diff_percent": round(diff_percent, 2)   # 변동률(%)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}