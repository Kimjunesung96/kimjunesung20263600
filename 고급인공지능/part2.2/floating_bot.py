import tkinter as tk
import pymysql
import threading
import time
import webbrowser
import random
import json
import os

# ---------------------------------------------------------
# 💡 설정 파일에서 알람 주기 읽어오기
# ---------------------------------------------------------
def get_alarm_interval():
    try:
        if os.path.exists("config.json"):
            with open("config.json", "r") as f:
                return int(json.load(f).get("alarm_interval", 10)) * 60 # 분을 초로 변환
    except:
        pass
    return 600 # 기본 10분

def get_top_10_news():
    try:
        conn = pymysql.connect(
            host='localhost', user='root', password='rla1dbs2',
            db='news_db', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
        )
        with conn.cursor() as cursor:
            cursor.execute("SELECT title, url FROM news ORDER BY created_at DESC LIMIT 30")
            result = list(cursor.fetchall())
        conn.close()
        
        if len(result) > 10:
            result = random.sample(result, 10)
        return result
    except Exception as e:
        print("DB 연결 에러:", e)
        return []

bubble_win = None
history_win = None
current_bubble_url = ""
last_toggle_time = 0 

def show_bubble(title, url, auto_hide=True):
    global bubble_win, current_bubble_url
    current_bubble_url = url
    
    if bubble_win and bubble_win.winfo_exists():
        bubble_win.destroy()
        
    bubble_win = tk.Toplevel(root)
    bubble_win.overrideredirect(True)
    bubble_win.attributes("-topmost", True)
    bubble_win.configure(bg='magenta')
    bubble_win.attributes("-transparentcolor", "magenta")
    
    short_title = title[:25] + "..." if len(title) > 25 else title
    lbl = tk.Label(
        bubble_win, text=f"🔔 [최신 뉴스 브리핑!]\n{short_title}", 
        bg="#e8f0fe", fg="#1a73e8", font=("맑은 고딕", 9, "bold"), 
        wraplength=200, relief="solid", bd=2, padx=10, pady=10, cursor="hand2"
    )
    lbl.pack()
    
    # 💡 개별 알림은 원문 사이트로!
    lbl.bind("<Button-1>", lambda e: open_and_close(current_bubble_url, "bubble"))

    bubble_win.update_idletasks()
    rx, ry, rw = root.winfo_x(), root.winfo_y(), root.winfo_width()
    bw, bh = bubble_win.winfo_reqwidth(), bubble_win.winfo_reqheight()
    sw = root.winfo_screenwidth()
    
    relative_rx = rx % sw
    if relative_rx + (rw // 2) + (bw // 2) > sw:
        bx = rx - bw + rw 
    else:
        bx = rx + (rw // 2) - (bw // 2) 

    by = ry - bh - 10
    bubble_win.geometry(f"+{bx}+{by}")
    
    if auto_hide:
        root.after(5000, hide_bubble)

def play_bubble_sequence(news_list, index=0):
    if index < len(news_list):
        news = news_list[index]
        show_bubble(news['title'], news['url'], auto_hide=False)
        root.after(5000, lambda: play_bubble_sequence(news_list, index + 1))
    else:
        hide_bubble()

def hide_bubble():
    global bubble_win
    if bubble_win and bubble_win.winfo_exists():
        bubble_win.destroy()
        bubble_win = None

def toggle_history_menu(event):
    global history_win, last_toggle_time
    
    current_time = time.time()
    if current_time - last_toggle_time < 0.5:
        return
    last_toggle_time = current_time
    
    if getattr(face_label, '_is_dragging', False):
        face_label._is_dragging = False
        return

    if history_win and history_win.winfo_exists():
        history_win.destroy()
        history_win = None
        return

    news_list = get_top_10_news()
    
    history_win = tk.Toplevel(root)
    history_win.overrideredirect(True)
    history_win.attributes("-topmost", True)
    history_win.configure(bg='magenta')
    history_win.attributes("-transparentcolor", "magenta")

    if not news_list:
        tk.Label(history_win, text="아직 뉴스가 없습니다.", bg="white", font=("맑은 고딕", 9)).pack(pady=2)
    else:
        tk.Label(
            history_win, text="📰 최근 주요 뉴스 브리핑", bg="#ffeb3b", 
            font=("맑은 고딕", 9, "bold"), relief="solid", bd=1, padx=5, pady=4
        ).pack(fill="x", pady=(0, 5))

        for news in news_list:
            short_title = news['title'][:25] + "..." if len(news['title']) > 25 else news['title']
            
            lbl = tk.Label(
                history_win, text=f"💬 {short_title}", bg="white", fg="#202124",
                font=("맑은 고딕", 9), wraplength=250, justify="left",
                relief="solid", bd=2, padx=10, pady=6, cursor="hand2"
            )
            lbl.pack(pady=3, fill="x")
            lbl.bind("<Enter>", lambda e, l=lbl: l.config(bg="#e8f0fe", fg="#1a73e8"))
            lbl.bind("<Leave>", lambda e, l=lbl: l.config(bg="white", fg="#202124"))
            
            # 💡 목록의 개별 기사도 원문 사이트로!
            lbl.bind("<Button-1>", lambda e, u=news['url']: open_and_close(u, "history"))

        # 💡 [핵심] 뉴스 전체보기(본사 이동) 버튼 추가!
        view_all_btn = tk.Label(
            history_win, text="🌐 뉴스 전체보기 (본사 이동)", bg="#e3f2fd", fg="#1a73e8", 
            font=("맑은 고딕", 9, "bold"), cursor="hand2", relief="solid", bd=1, padx=5, pady=4
        )
        view_all_btn.pack(fill="x", pady=(5, 0))
        view_all_btn.bind("<Button-1>", lambda e: open_and_close("http://localhost:5173", "history"))

        close_btn = tk.Label(
            history_win, text="❌ 비서 퇴근시키기", bg="#ffcdd2", 
            font=("맑은 고딕", 9, "bold"), cursor="hand2", relief="solid", bd=1, padx=5, pady=4
        )
        close_btn.pack(fill="x", pady=(5, 0))
        close_btn.bind("<Button-1>", lambda e: root.destroy())

    history_win.update_idletasks()
    rx, ry, rw = root.winfo_x(), root.winfo_y(), root.winfo_width()
    hw, hh = history_win.winfo_reqwidth(), history_win.winfo_reqheight()
    sw = root.winfo_screenwidth()
    
    relative_rx = rx % sw 
    if relative_rx + (rw // 2) + (hw // 2) > sw:
        hx = rx - hw + rw 
    else:
        hx = rx + (rw // 2) - (hw // 2)

    hy = ry - hh - 10
    history_win.geometry(f"+{hx}+{hy}")

# 💡 인자로 받은 url(본사 주소 또는 구글 원문)로 각각 이동하게 수정
def open_and_close(url, win_type):
    global history_win, bubble_win
    webbrowser.open(url) 
    
    if win_type == "history" and history_win and history_win.winfo_exists():
        history_win.destroy()
        history_win = None
    elif win_type == "bubble" and bubble_win and bubble_win.winfo_exists():
        bubble_win.destroy()
        bubble_win = None

def on_press(event):
    face_label._drag_start_x = event.x
    face_label._drag_start_y = event.y
    face_label._is_dragging = False

def on_drag(event):
    global history_win, bubble_win
    
    dx = abs(event.x - face_label._drag_start_x)
    dy = abs(event.y - face_label._drag_start_y)
    
    if dx > 5 or dy > 5:
        if not getattr(face_label, '_is_dragging', False):
            if history_win and history_win.winfo_exists():
                history_win.destroy()
                history_win = None
            if bubble_win and bubble_win.winfo_exists():
                bubble_win.destroy()
                bubble_win = None
            face_label._is_dragging = True
            
        x = root.winfo_x() - face_label._drag_start_x + event.x
        y = root.winfo_y() - face_label._drag_start_y + event.y
        root.geometry(f"+{x}+{y}")

# ---------------------------------------------------------
# 💡 설정된 알람 주기를 실시간으로 읽어와서 적용하는 엔진
# ---------------------------------------------------------
def fetch_news_loop():
    time.sleep(2)
    while True:
        try:
            conn = pymysql.connect(
                host='localhost', user='root', password='rla1dbs2',
                db='news_db', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
            )
            with conn.cursor() as cursor:
                cursor.execute("SELECT title, url FROM news ORDER BY created_at DESC LIMIT 30")
                hourly_30_news = list(cursor.fetchall())
            conn.close()
        except Exception as e:
            hourly_30_news = []

        if len(hourly_30_news) >= 10:
            ten_news = random.sample(hourly_30_news, 10)
            root.after(0, lambda: play_bubble_sequence(ten_news, 0))
        
        # 리액트에서 설정한 최신 주기를 여기서 가져옵니다.
        interval_seconds = get_alarm_interval()
        
        # 설정이 바뀌면 바로바로 눈치챌 수 있도록 5초 단위로 쪼개서 대기합니다!
        for _ in range(int(interval_seconds / 5)):
            time.sleep(5)

root = tk.Tk()
root.geometry("+1500+800") 
root.overrideredirect(True)
root.attributes("-topmost", True)
root.configure(bg='magenta')
root.attributes("-transparentcolor", "magenta")

face_label = tk.Label(root, text="🤖", font=("Arial", 45), bg="magenta", cursor="fleur")
face_label.pack()

face_label.bind("<ButtonPress-1>", on_press)
face_label.bind("<B1-Motion>", on_drag)
face_label.bind("<ButtonRelease-1>", toggle_history_menu)

threading.Thread(target=fetch_news_loop, daemon=True).start()
root.mainloop()