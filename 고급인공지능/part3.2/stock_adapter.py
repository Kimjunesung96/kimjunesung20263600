import yfinance as yf
import math
import requests
from bs4 import BeautifulSoup


def fix_nan(data):
    if isinstance(data, float) and math.isnan(data): return 0
    if isinstance(data, dict): return {k: fix_nan(v) for k, v in data.items()}
    if isinstance(data, list): return [fix_nan(v) for v in data]
    return data


def get_krx_realtime_naver(ticker_code):
    """네이버 금융에서 실시간 가격 긁어오기 (가입 ❌, 완전 무료 ⭕)"""

    pure_code = ticker_code.split('.')[0]   # '005930.KS' → '005930'

    url = f"https://finance.naver.com/item/main.naver?code={pure_code}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    res = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(res.text, 'html.parser')

    try:
        today_p = soup.select_one('.no_today .blind')
        price = float(today_p.text.replace(',', ''))

        exday_spans  = soup.select('.no_exday .blind')
        diff         = float(exday_spans[0].text.replace(',', ''))
        diff_percent = float(exday_spans[1].text.replace(',', '').replace('%', ''))

        exday_html = str(soup.select_one('.no_exday'))
        if '하락' in exday_html or 'nv01' in exday_html or 'down' in exday_html:
            diff         = -abs(diff)
            diff_percent = -abs(diff_percent)

        return {
            "status": "success",
            "price": price,
            "diff": diff,
            "diff_percent": round(diff_percent, 2)
        }

    except Exception as e:
        raise Exception(f"네이버 금융 파싱 에러: {str(e)}")


def get_realtime_stock(ticker: str):
    """티커를 받아서 한국은 네이버로, 미국/코인은 야후로 분기 처리"""
    try:
        # 💡 한국 주식(.KS, .KQ)은 네이버 금융 실시간
        if ticker.endswith(".KS") or ticker.endswith(".KQ"):
            return fix_nan(get_krx_realtime_naver(ticker))

        # 💡 미국 주식 / 코인은 yfinance
        stock = yf.Ticker(ticker)
        hist  = stock.history(period="7d")   # 7d: 주말·공휴일 연속돼도 안전

        if len(hist) < 2:
            return fix_nan({"status": "error", "message": "데이터 없음"})

        prev_close = float(hist['Close'].iloc[-2])

        current_price = None
        try:
            current_price = stock.fast_info.last_price
        except Exception:
            pass
        if not current_price or (isinstance(current_price, float) and math.isnan(current_price)):
            current_price = float(hist['Close'].iloc[-1])

        diff         = current_price - prev_close
        diff_percent = (diff / prev_close) * 100 if prev_close else 0

        return fix_nan({
            "status": "success",
            "price": round(float(current_price), 2),
            "diff": round(float(diff), 2),
            "diff_percent": round(float(diff_percent), 2)
        })

    except Exception as e:
        return fix_nan({"status": "error", "message": str(e)})