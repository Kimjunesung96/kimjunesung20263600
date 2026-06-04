import tkinter as tk
import threading
import ctypes
import sqlite3
from core.settings import get_settings
from core.database import init_db, get_db_connection
from core.event_handler import BotEventHandler
from ui.bubble_ui import BubbleUI
from ui.toolbar_ui import ToolbarUI
from ui.history_ui import HistoryUI
from features.voice_listener import VoiceListener
from bot_features import AssistantFeatures

# 💡 [복구] 뉴스 DB 조회 함수
def get_news_from_db(limit, keyword=""):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT title, url FROM news"
        params = []
        if keyword:
            query += " WHERE title LIKE ? OR ai_summary LIKE ?"
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        cursor.execute(query, params)
        result = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return result
    except: return []

def fetch_news_loop(bot, bubble):
    import time, random
    while True:
        bot.check_alarm()
        s = get_settings()
        news = get_news_from_db(30, s["custom_keyword"])
        if news:
            sample = random.sample(news, min(len(news), s["news_count"]))
            root.after(0, lambda: bubble.play_sequence(sample, 0, s["bubble_duration"]))
        time.sleep(s["alarm_interval"])

if __name__ == "__main__":
    try: ctypes.windll.user32.SetProcessDPIAware()
    except: pass
    init_db()
    root = tk.Tk()
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry(f"+{sw-150}+{sh-150}")
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.configure(bg='#202124')

    face_label = tk.Label(root, text="🤖", font=("Arial", 45), bg="#202124", fg="white", cursor="fleur")
    face_label.pack(side="bottom")

    bubble = BubbleUI(root, None)
    bot = AssistantFeatures(root, face_label, bubble.show)
    bubble.bot = bot
    
    # 💡 [해결] 툴바와 뉴스창에 필요한 함수들을 제대로 전달
    def open_and_close(url, win_type):
        import webbrowser
        if url: webbrowser.open(url)
        if win_type == "history": history.hide()

    toolbar = ToolbarUI(root, bot)
    # 핵심: get_news_from_db와 open_and_close를 역사창(HistoryUI)에 주입
    history = HistoryUI(root, get_news_from_db, open_and_close)
    
    handler = BotEventHandler(root, face_label, bot)
    voice = VoiceListener(bot, bubble.show)
    voice.start()

    def close_all():
        toolbar.hide(); history.hide(); bubble.hide()

    face_label.bind("<ButtonPress-1>", handler.on_press)
    face_label.bind("<B1-Motion>", lambda e: handler.on_drag(e, close_all))
    face_label.bind("<ButtonRelease-1>", lambda e: [history.toggle(), toolbar.toggle()] if not getattr(face_label, '_is_dragging', False) else None)

    threading.Thread(target=fetch_news_loop, args=(bot, bubble), daemon=True).start()
    root.mainloop()