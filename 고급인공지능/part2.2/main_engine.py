import schedule
import time
import requests
import datetime
import sqlite3
import xml.etree.ElementTree as ET
import re

# ---------------------------------------------------------
# DB 연결 함수
# ---------------------------------------------------------
def get_db_connection():
    conn = sqlite3.connect('news.db')
    # 테이블이 없으면 최초 1회 자동 생성하는 똑똑한 코드 추가
    conn.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id TEXT PRIMARY KEY,
            category_code TEXT,
            title TEXT,
            url TEXT,
            ai_summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    return conn

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html).strip()

def generate_news_id(category_code, sequence):
    now = datetime.datetime.now()
    return f"{now.strftime('%y%m%d')}{category_code}{now.strftime('%H')}{str(sequence).zfill(3)}"

# ---------------------------------------------------------
# 8개 분야 자동 수집 파이프라인
# ---------------------------------------------------------
def fetch_all_categories():
    print(f"\n[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📡 전 분야 뉴스 수집 시작...")
    
    # 분야별 구글 뉴스 RSS 주소 (8종 풀세트)
    RSS_URLS = {
        "01": "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=ko&gl=KR&ceid=KR:ko", # IT/테크
        "02": "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=ko&gl=KR&ceid=KR:ko",   # 경제
        "03": "https://news.google.com/rss/headlines/section/topic/NATION?hl=ko&gl=KR&ceid=KR:ko",     # 사회
        "04": "https://news.google.com/rss/headlines/section/topic/WORLD?hl=ko&gl=KR&ceid=KR:ko",      # 세계
        "05": "https://news.google.com/rss/headlines/section/topic/ENTERTAINMENT?hl=ko&gl=KR&ceid=KR:ko", # 연예
        "06": "https://news.google.com/rss/headlines/section/topic/SPORTS?hl=ko&gl=KR&ceid=KR:ko",      # 스포츠
        "07": "https://news.google.com/rss/headlines/section/topic/SCIENCE?hl=ko&gl=KR&ceid=KR:ko",     # 과학
        "08": "https://news.google.com/rss/headlines/section/topic/HEALTH?hl=ko&gl=KR&ceid=KR:ko"       # 건강
    }
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        for cat_code, url in RSS_URLS.items():
            print(f"[{cat_code}] 카테고리 수집 중...")
            response = requests.get(url)
            root = ET.fromstring(response.text)
            items = root.findall('.//item')[:10] # 각 카테고리별 상위 10개만 깔끔하게!
            
            sequence = 1
            for item in items:
                title = item.find('title').text
                link = item.find('link').text
                raw_desc = item.find('description').text
                ai_summary = clean_html(raw_desc) if raw_desc else "요약 없음"
                news_id = generate_news_id(cat_code, sequence)
                
                # INSERT OR IGNORE로 중복 수집 방지 (SQLite 전용 문법)
                sql = """
                INSERT OR IGNORE INTO news (id, category_code, title, url, ai_summary)
                VALUES (?, ?, ?, ?, ?)
                """
                cursor.execute(sql, (news_id, cat_code, title, link, ai_summary))
                sequence += 1
                
        conn.commit()
        print("✅ 8개 분야 모두 수집 및 DB 저장 완료!")  # ✅ 수정: 3개 → 8개
        
    except Exception as e:
        print(f"❌ 수집 에러 발생: {e}")
    finally:
        conn.close()

# ---------------------------------------------------------
# 타이머 설정 (10분마다 실행)
# ---------------------------------------------------------
schedule.every(10).minutes.do(fetch_all_categories)

if __name__ == "__main__":
    fetch_all_categories() # 파일 실행하자마자 바로 1회 가동
    
    # 스케줄러 무한 대기열
    while True:
        schedule.run_pending()
        time.sleep(1)