import sqlite3

def get_db_connection():
    """
    멀티스레딩 환경에서 안전하게 SQLite에 접속하고 WAL 모드를 활성화합니다.
    """
    conn = sqlite3.connect('news.db', timeout=30, check_same_thread=False)
    # WAL 모드: 읽기와 쓰기를 동시에 처리하여 성능 최적화
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    시스템 가동 시 필요한 테이블들을 생성하고 초기 데이터를 삽입합니다.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. 일정 테이블
    cursor.execute('CREATE TABLE IF NOT EXISTS schedule (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT NOT NULL, content TEXT NOT NULL)')
    
    # 2. 클립보드 테이블
    cursor.execute('CREATE TABLE IF NOT EXISTS clipboard (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT NOT NULL, content TEXT NOT NULL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)')
    
    # 3. 관심 주식 테이블
    cursor.execute('CREATE TABLE IF NOT EXISTS favorite_stocks (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, ticker TEXT NOT NULL UNIQUE)')
    
    # 초기 주식 데이터 샘플 삽입
    cursor.execute("SELECT COUNT(*) FROM favorite_stocks")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO favorite_stocks (name, ticker) VALUES ('애플', 'AAPL')")
        cursor.execute("INSERT INTO favorite_stocks (name, ticker) VALUES ('테슬라', 'TSLA')")
        cursor.execute("INSERT INTO favorite_stocks (name, ticker) VALUES ('삼성전자', '005930.KS')")
        
    conn.commit()
    conn.close()