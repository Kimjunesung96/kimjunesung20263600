from flask import Flask, jsonify, request, render_template
from scheduler import start_background_scheduler

app = Flask(__name__)

# 서버 구동 시 스케줄러 시작
start_background_scheduler() 

@app.route('/')
def index():
    # 프론트엔드 화면(index.html) 연결
    return render_template('index.html')

@app.route('/api/news', methods=['GET'])
def get_daily_news():
    dummy_response = [
        {"id": 1, "title": "[속보] 새로운 AI 모델 발표", "summary": "기존보다 10배 빠른 AI 등장.", "url": "#", "is_ad": False},
        {"id": 2, "title": "특가 할인 찬스!", "summary": "관심 주제 맞춤형 광고입니다.", "url": "#", "is_ad": True}
    ]
    return jsonify({"status": "success", "data": dummy_response})

@app.route('/api/user/settings', methods=['POST'])
def update_user_settings():
    user_data = request.json
    selected_topics = user_data.get('topics')
    alarm_time = user_data.get('time')
    # TODO: DB 저장 로직
    return jsonify({"status": "success", "message": "설정 저장 완료"})

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)