import schedule
import time
import requests
import datetime
import sqlite3
import xml.etree.ElementTree as ET
import re
import email.utils
from datetime import datetime as dt, timedelta, timezone

KST = timezone(timedelta(hours=9))

def get_db_connection():
    conn = sqlite3.connect('news.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id TEXT PRIMARY KEY,
            category_code TEXT,
            title TEXT,
            url TEXT UNIQUE,
            ai_summary TEXT,
            created_at TEXT
        )
    ''')
    return conn

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html).strip()

def parse_rss_date(date_str):
    try:
        dt_obj = email.utils.parsedate_to_datetime(date_str)
        return dt_obj.astimezone(KST).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return datetime.datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')

def fetch_all_categories():
    print(f"\n[{datetime.datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')}] 📡 뉴스 수집 시작...")
    
    RSS_URLS = {
        "01": "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=ko&gl=KR&ceid=KR:ko",
        "02": "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=ko&gl=KR&ceid=KR:ko",
        "03": "https://news.google.com/rss/headlines/section/topic/NATION?hl=ko&gl=KR&ceid=KR:ko",
        "04": "https://news.google.com/rss/headlines/section/topic/WORLD?hl=ko&gl=KR&ceid=KR:ko",
        "05": "https://news.google.com/rss/headlines/section/topic/ENTERTAINMENT?hl=ko&gl=KR&ceid=KR:ko",
        "06": "https://news.google.com/rss/headlines/section/topic/SPORTS?hl=ko&gl=KR&ceid=KR:ko",
        "07": "https://news.google.com/rss/headlines/section/topic/SCIENCE?hl=ko&gl=KR&ceid=KR:ko",
        "08": "https://news.google.com/rss/headlines/section/topic/HEALTH?hl=ko&gl=KR&ceid=KR:ko"
    }
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ 기존 DB에 url UNIQUE 제약이 없을 경우를 대비해 인덱스로 추가
    try:
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_news_url ON news(url)")
    except Exception:
        pass
    
    try:
        # 💡 [추가] 구글 서버가 봇으로 인식해 연결을 끊는 것을 방지하기 위한 신분증(User-Agent)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        for cat_code, url in RSS_URLS.items():
            print(f"[{cat_code}] 카테고리 수집 중...")
            response = requests.get(url, headers=headers) # 🚨 [변경] 요청 시 신분증 제시
            root = ET.fromstring(response.text)
            items = root.findall('.//item')[:10]
            
            sequence = 1
            for item in items:
                title = item.find('title').text
                link = item.find('link').text
                raw_desc = item.find('description').text
                pub_date_str = item.find('pubDate').text
                
                ai_summary = clean_html(raw_desc) if raw_desc else "요약 없음"
                formatted_created_at = parse_rss_date(pub_date_str)

                # ✅ url 기준 중복 방지 — 같은 기사가 몇 번이든 다시 들어오지 않음
                sql = """
                INSERT OR IGNORE INTO news (id, category_code, title, url, ai_summary, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """
                # id는 url을 해시해서 고유하게 생성
                import hashlib
                news_id = hashlib.md5(link.encode()).hexdigest()[:16]
                cursor.execute(sql, (news_id, cat_code, title, link, ai_summary, formatted_created_at))
                sequence += 1
                
        conn.commit()
        print("✅ 수집 완료!")
        
    except Exception as e:
        print(f"❌ 수집 에러 발생: {e}")
    finally:
        conn.close()

schedule.every(10).minutes.do(fetch_all_categories)

if __name__ == "__main__":
    fetch_all_categories()
    
    while True:
        schedule.run_pending()
        time.sleep(1)