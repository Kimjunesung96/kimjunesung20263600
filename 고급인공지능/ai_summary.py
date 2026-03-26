import requests
import json

def get_gemini_summary(news_content):
    API_KEY = "여기에_발급받은_API_키_입력" 
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}"
    
    prompt = f"다음 뉴스 기사 본문을 읽고, 독자가 흥미를 가질 수 있도록 핵심만 딱 1줄로 요약해 줘.\n\n[기사 본문]\n{news_content}"
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status() 
        
        result = response.json()
        summary_text = result['candidates']['content']['parts']['text']
        return summary_text
        
    except Exception as e:
        print(f"API 요청 오류: {e}")
        return "요약 실패"