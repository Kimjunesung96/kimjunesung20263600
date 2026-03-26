import time
from apscheduler.schedulers.background import BackgroundScheduler
# from crawler import crawl_news_by_topic
# from ai_summary import get_gemini_summary

TOPICS = ['IT', '경제', '사회', '세계', '연예', '스포츠']
current_topic_index = 0

def crawl_news_rotation():
    global current_topic_index
    target_topic = TOPICS[current_topic_index]
    print(f"[5분 주기 크롤러] 현재 수집 주제: {target_topic}")
    # crawl_news_by_topic(target_topic)
    current_topic_index = (current_topic_index + 1) % len(TOPICS)

def summarize_news_with_gemini():
    print("[10분 주기 AI 요약] 빈칸 데이터 20개 탐색 및 요약 진행")
    # TODO: DB 조회 후 for문으로 get_gemini_summary() 호출

def send_push_notification():
    print("[1시간 주기 정기 알림] 맞춤형 뉴스 10개 및 광고 전송")
    # TODO: DB에서 데이터 추출 후 알림 발송

def start_background_scheduler():
    scheduler = BackgroundScheduler(timezone="Asia/Seoul")
    scheduler.add_job(crawl_news_rotation, 'interval', minutes=5, id='job_crawler')
    scheduler.add_job(summarize_news_with_gemini, 'interval', minutes=10, id='job_summary')
    scheduler.add_job(send_push_notification, 'cron', minute=0, id='job_notification')
    
    scheduler.start()
    print("=== 뉴스 백엔드 스케줄러 작동 시작 ===")