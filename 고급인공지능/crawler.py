import requests
from bs4 import BeautifulSoup

def crawl_news_by_topic(topic):
    url = f"https://news.example.com/category/{topic}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('div', class_='news_item', limit=10) 
        
        for article in articles:
            title_tag = article.find('a', class_='title')
            title = title_tag.text.strip()
            link = title_tag['href']
            
            is_breaking_news = False
            if "[속보]" in title or "[단독]" in title or "[특보]" in title:
                is_breaking_news = True
                print(f"🚨 특보 감지: {title}")
                # TODO: 특보 즉시 처리 로직
                
            # TODO: DB 저장 로직 (id, 시간, 주제, 제목, 링크, 특보여부 등)
            print(f"저장 완료: [{topic}] {title}")
            
    except Exception as e:
        print(f"크롤링 중 오류 발생: {e}")