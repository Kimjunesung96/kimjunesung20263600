import tkinter as tk
import sqlite3
import threading
import time
import webbrowser
import random
import json
import os

from bot_features import AssistantFeatures

def get_settings():
    try:
        if os.path.exists("config.json"):
            with open("config.json", "r") as f:
                data = json.load(f)
                return {
                    "alarm_interval": int(data.get("alarm_interval", 10)) * 60,
                    "bubble_duration": int(data.get("bubble_duration", 5)) * 1000,
                    "news_count": int(data.get("news_count", 10)),
                    "custom_keyword": data.get("custom_keyword", "")
                }
    except: pass
    return {"alarm_interval": 600, "bubble_duration": 5000, "news_count": 10, "custom_keyword": ""}

def save_custom_keyword(keyword):
    data = {}
    if os.path.exists("config.json"):
        try:
            with open("config.json", "r") as f: data = json.load(f)
        except: pass
    data["custom_keyword"] = keyword
    with open("config.json", "w") as f: json.dump(data, f)

def get_news_from_db(limit, keyword=""):
    try:
        conn = sqlite3.connect('news.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        query = "SELECT title, url FROM news"
        params = []
        if keyword:
            query += " WHERE title LIKE ? OR ai_summary LIKE ?"
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        query += " ORDER BY created_at DESC"
        query += f" LIMIT {50 if limit == 0 else limit}"
        cursor.execute(query, params)
        result = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return result
    except Exception as e: return []

bubble_win = None
history_win = None
toolbar_win = None  
current_bubble_url = ""
last_toggle_time = 0 

# ---------------------------------------------------------
# 💡 말풍선 팝업 UI
# ---------------------------------------------------------
def show_bubble(title, url, duration_ms, auto_hide=True):
    global bubble_win, current_bubble_url
    current_bubble_url = url
    
    if bubble_win and bubble_win.winfo_exists(): bubble_win.destroy()
        
    bubble_win = tk.Toplevel(root)
    bubble_win.overrideredirect(True)
    bubble_win.attributes("-topmost", True)
    bubble_win.configure(bg='magenta')
    bubble_win.attributes("-transparentcolor", "magenta")
    
    short_title = title[:30] + "..." if len(title) > 30 else title
    
    if url == "TIMER": header_text, bg_color, fg_color = "⏳ [타이머 종료!]", "#ffeb3b", "#d32f2f"
    elif url == "ALARM": header_text, bg_color, fg_color = "⏰ [알람 시간입니다!]", "#fce4ec", "#c2185b"
    else: header_text, bg_color, fg_color = "🔔 [최신 뉴스 브리핑!]", "#e8f0fe", "#1a73e8"

    lbl = tk.Label(bubble_win, text=f"{header_text}\n{short_title}", bg=bg_color, fg=fg_color, font=("맑은 고딕", 9, "bold"), wraplength=200, relief="solid", bd=2, padx=10, pady=10, cursor="hand2")
    lbl.pack()
    lbl.bind("<Button-1>", lambda e: open_and_close(current_bubble_url, "bubble"))
    bubble_win.update_idletasks()
    
    rx, ry, rw = root.winfo_x(), root.winfo_y(), root.winfo_width()
    bw, bh = bubble_win.winfo_reqwidth(), bubble_win.winfo_reqheight()
    sw = root.winfo_screenwidth()
    
    bx = rx + (rw // 2) - (bw // 2)
    if bx + bw > sw: bx = sw - bw - 5
    if bx < 0: bx = 5
    
    # 💡 [핵심] 머리 위에 떠 있는 모든 타워들 중 '가장 높은 곳(y좌표가 가장 작은 값)'을 찾습니다!
    highest_y = ry
    if bot.todo_win and bot.todo_win.winfo_exists(): 
        highest_y = min(highest_y, bot.todo_win.winfo_y())
    if hasattr(bot, 'folder_win') and bot.folder_win and bot.folder_win.winfo_exists(): 
        highest_y = min(highest_y, bot.folder_win.winfo_y())
    if hasattr(bot, 'stock_win') and bot.stock_win and bot.stock_win.winfo_exists(): 
        highest_y = min(highest_y, bot.stock_win.winfo_y())
        
    by = highest_y - bh - 10 
    
    bubble_win.geometry(f"+{bx}+{by}")
    if auto_hide: root.after(duration_ms, hide_bubble)

def play_bubble_sequence(news_list, index, duration_ms):
    if index < len(news_list):
        news = news_list[index]
        show_bubble(news['title'], news['url'], duration_ms, auto_hide=False)
        root.after(duration_ms, lambda: play_bubble_sequence(news_list, index + 1, duration_ms))
    else: hide_bubble()

def hide_bubble():
    global bubble_win
    if bubble_win and bubble_win.winfo_exists(): bubble_win.destroy(); bubble_win = None

# ---------------------------------------------------------
# 위쪽: 뉴스 목록 창
# ---------------------------------------------------------
def open_history_menu():
    global history_win
    if history_win and history_win.winfo_exists(): history_win.destroy()
    
    settings = get_settings()
    history_win = tk.Toplevel(root)
    history_win.overrideredirect(True)
    history_win.attributes("-topmost", True)
    history_win.configure(bg='magenta')
    history_win.attributes("-transparentcolor", "magenta")

    main_frame = tk.Frame(history_win, bg="white", relief="solid", bd=2)
    main_frame.pack(fill="both", expand=True)
    tk.Label(main_frame, text="📰 맞춤형 뉴스 브리핑", bg="#ffeb3b", fg="black", font=("맑은 고딕", 9, "bold"), padx=5, pady=6).pack(fill="x", side="top")

    search_frame = tk.Frame(main_frame, bg="#f1f3f4", padx=5, pady=5)
    search_frame.pack(fill="x", side="top")
    tk.Label(search_frame, text="관심 키워드:", bg="#f1f3f4", font=("맑은 고딕", 8, "bold")).pack(side="left")
    search_var = tk.StringVar(value=settings["custom_keyword"])
    search_entry = tk.Entry(search_frame, textvariable=search_var, font=("맑은 고딕", 9), relief="solid", bd=1)
    search_entry.pack(side="left", fill="x", expand=True, padx=(5, 5), ipady=2)
    
    def apply_custom_keyword():
        kw = search_var.get().strip()
        save_custom_keyword(kw) 
        load_news_list(kw)      
        
    tk.Button(search_frame, text="적용", font=("맑은 고딕", 8, "bold"), bg="#1a73e8", fg="white", relief="flat", cursor="hand2", command=apply_custom_keyword).pack(side="right", ipady=1)
    search_entry.bind("<Return>", lambda e: apply_custom_keyword())

    bottom_frame = tk.Frame(main_frame, bg="white")
    bottom_frame.pack(fill="x", side="bottom")
    resizer = tk.Label(bottom_frame, text="◢", font=("Arial", 14), bg="white", fg="#b0b0b0", cursor="size_nw_se")
    resizer.pack(side="right", anchor="se", padx=5)

    btn_frame = tk.Frame(bottom_frame, bg="white")
    btn_frame.pack(side="left", fill="x", expand=True)
    tk.Label(btn_frame, text="🌐 리액트 대시보드 열기", bg="#e3f2fd", fg="#1a73e8", font=("맑은 고딕", 9, "bold"), cursor="hand2", padx=5, pady=8).pack(fill="x", pady=(5, 0))
    btn_frame.winfo_children()[-1].bind("<Button-1>", lambda e: open_and_close("http://localhost:5173", "history"))

    middle_frame = tk.Frame(main_frame, bg="white")
    middle_frame.pack(fill="both", expand=True, side="top")

    canvas = tk.Canvas(middle_frame, bg="white", highlightthickness=0, width=290, height=350)
    scrollbar = tk.Scrollbar(middle_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="white")
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(frame_id, width=e.width))
    canvas.configure(yscrollcommand=scrollbar.set)
    history_win.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def load_news_list(keyword=""):
        for widget in scrollable_frame.winfo_children(): widget.destroy()
        items = get_news_from_db(settings["news_count"], keyword)
        if not items:
            tk.Label(scrollable_frame, text=f"'{keyword}' 관련 뉴스가 없습니다." if keyword else "아직 뉴스가 없습니다.", bg="white", font=("맑은 고딕", 9)).pack(pady=20)
        else:
            for item in items:
                lbl = tk.Label(scrollable_frame, text=f"💬 {item['title']}", bg="white", fg="#202124", font=("맑은 고딕", 9), anchor="w", relief="solid", bd=1, padx=5, pady=8, cursor="hand2")
                lbl.pack(pady=2, padx=5, fill="x") 
                lbl.bind("<Enter>", lambda e, l=lbl: l.config(bg="#e8f0fe", fg="#1a73e8"))
                lbl.bind("<Leave>", lambda e, l=lbl: l.config(bg="white", fg="#202124"))
                lbl.bind("<Button-1>", lambda e, u=item['url']: open_and_close(u, "history"))
        canvas.yview_moveto(0)

    load_news_list(settings["custom_keyword"])

    def start_resize(e):
        history_win._resize_start_x = e.x_root; history_win._resize_start_y = e.y_root
        history_win._init_width = history_win.winfo_width(); history_win._init_height = history_win.winfo_height()
        history_win._x = history_win.winfo_x(); history_win._y = history_win.winfo_y()

    def do_resize(e):
        new_w = max(250, history_win._init_width + (e.x_root - history_win._resize_start_x))
        new_h = max(200, history_win._init_height + (e.y_root - history_win._resize_start_y))
        history_win.geometry(f"{new_w}x{new_h}+{history_win._x}+{history_win._y}")

    resizer.bind("<ButtonPress-1>", start_resize)
    resizer.bind("<B1-Motion>", do_resize)
    history_win.update_idletasks()
    
    rx, ry, rw = root.winfo_x(), root.winfo_y(), root.winfo_width()
    hw, hh = history_win.winfo_reqwidth(), history_win.winfo_reqheight()
    sw = root.winfo_screenwidth()
    
    if rx + rw + hw + 5 <= sw: hx = rx + rw + 5
    elif rx - hw - 5 >= 0: hx = rx - hw - 5
    else: hx = sw - hw
    history_win.geometry(f"+{hx}+{ry - hh - 10}")

# ---------------------------------------------------------
# 옆쪽: 리모컨(툴바) 메뉴
# ---------------------------------------------------------
def open_toolbar_menu():
    global toolbar_win
    if toolbar_win and toolbar_win.winfo_exists(): toolbar_win.destroy()
    
    toolbar_win = tk.Toplevel(root)
    toolbar_win.overrideredirect(True)
    toolbar_win.attributes("-topmost", True)
    toolbar_win.configure(bg='magenta')
    toolbar_win.attributes("-transparentcolor", "magenta")

    bar_frame = tk.Frame(toolbar_win, bg="#202124", padx=10, pady=5, relief="flat", bd=0)
    bar_frame.pack()

    btn_style = {"bg": "#3c4043", "fg": "white", "font": ("맑은 고딕", 9, "bold"), "relief": "flat", "cursor": "hand2", "padx": 8, "pady": 5}
    sub_btn_style = {"bg": "#1a73e8", "fg": "white", "font": ("맑은 고딕", 9, "bold"), "relief": "flat", "cursor": "hand2", "padx": 6, "pady": 4}

    def update_toolbar_position():
        toolbar_win.update_idletasks()
        sw = root.winfo_screenwidth()
        rx, ry, rw = root.winfo_x(), root.winfo_y(), root.winfo_width()
        tw, th = toolbar_win.winfo_reqwidth(), toolbar_win.winfo_reqheight()

        if rx + rw + tw + 5 <= sw: x = rx + rw + 5
        elif rx - tw - 5 >= 0: x = rx - tw - 5
        else: x = sw - tw 
        y = ry + (root.winfo_height() // 2) - (th // 2)
        toolbar_win.geometry(f"+{x}+{y}")

    def start_and_close(m):
        bot.start_timer(m)
        open_and_close("", "toolbar")

    def start_custom_timer(val):
        try:
            m = int(val)
            if m > 0: start_and_close(m)
        except: pass

    def draw_timer_toolbar():
        for w in bar_frame.winfo_children(): w.destroy()
        tk.Button(bar_frame, text="1분", command=lambda: start_and_close(1), **sub_btn_style).pack(side="left", padx=2)
        tk.Button(bar_frame, text="3분", command=lambda: start_and_close(3), **sub_btn_style).pack(side="left", padx=2)
        tk.Button(bar_frame, text="5분", command=lambda: start_and_close(5), **sub_btn_style).pack(side="left", padx=2)
        tk.Button(bar_frame, text="10분", command=lambda: start_and_close(10), **sub_btn_style).pack(side="left", padx=2)
        custom_var = tk.StringVar()
        entry = tk.Entry(bar_frame, textvariable=custom_var, width=4, font=("맑은 고딕", 10, "bold"), justify="center", bd=0)
        entry.pack(side="left", padx=(8, 2), ipady=4)
        tk.Button(bar_frame, text="확인", command=lambda: start_custom_timer(custom_var.get()), bg="#34a853", fg="white", font=("맑은 고딕", 9, "bold"), relief="flat", cursor="hand2").pack(side="left", padx=2, ipady=1)
        tk.Button(bar_frame, text="🔙", command=draw_main_toolbar, bg="#5f6368", fg="white", font=("맑은 고딕", 9), relief="flat", cursor="hand2", padx=5).pack(side="left", padx=(10, 0))
        update_toolbar_position()

    def draw_main_toolbar():
        for w in bar_frame.winfo_children(): w.destroy()
        if not bot.is_timer_running: tk.Button(bar_frame, text="⏳ 타이머", command=draw_timer_toolbar, **btn_style).pack(side="left", padx=3)
        else: tk.Button(bar_frame, text="🛑 정지", command=lambda: [bot.stop_timer(), open_and_close("", "toolbar")], **btn_style).pack(side="left", padx=3)
        tk.Button(bar_frame, text="⏰ 알람", command=lambda: [bot.set_alarm(), open_and_close("", "toolbar")], **btn_style).pack(side="left", padx=3)
        
        # 💡 [핵심] 리모컨 버튼 5총사 정렬 (달력, 캡처, 폴더, 주식, 닫기)
        tk.Button(bar_frame, text="📅 달력", command=bot.toggle_todo_bubbles, **btn_style).pack(side="left", padx=3)
        tk.Button(bar_frame, text="📸 캡처", command=lambda: [open_and_close("", "toolbar"), bot.start_screenshot()], **btn_style).pack(side="left", padx=3)
        tk.Button(bar_frame, text="📁 폴더", command=bot.toggle_folder_bubbles, **btn_style).pack(side="left", padx=3)
        tk.Button(bar_frame, text="📈 주식", command=bot.toggle_stock_bubbles, **btn_style).pack(side="left", padx=3)
        tk.Button(bar_frame, text="✖ 닫기", command=lambda: toggle_all_menus(None), bg="#ea4335", fg="white", font=("맑은 고딕", 9, "bold"), relief="flat", cursor="hand2", padx=8, pady=5).pack(side="left", padx=(10,3))
        
        update_toolbar_position()

    draw_main_toolbar()

# ---------------------------------------------------------
# 원터치 통합 제어 기능
# ---------------------------------------------------------
def toggle_all_menus(event=None):
    global history_win, toolbar_win, last_toggle_time
    if event:
        if getattr(face_label, '_is_dragging', False):
            face_label._is_dragging = False; return
        if time.time() - last_toggle_time < 0.5: return
        last_toggle_time = time.time()

    is_open = (history_win and history_win.winfo_exists()) or (toolbar_win and toolbar_win.winfo_exists())
    if is_open:
        if history_win: history_win.destroy(); history_win = None
        if toolbar_win: toolbar_win.destroy(); toolbar_win = None
    else:
        open_history_menu()
        open_toolbar_menu()

def open_and_close(url, win_type):
    global history_win, bubble_win, toolbar_win
    if url and url not in ["TIMER", "ALARM"]: webbrowser.open(url) 
    if win_type in ["history", "toolbar"]:
        if history_win: history_win.destroy(); history_win = None
        if toolbar_win: toolbar_win.destroy(); toolbar_win = None
    if win_type == "bubble" and bubble_win: bubble_win.destroy(); bubble_win = None

# ---------------------------------------------------------
# 마우스 조작 및 알림 루프
# ---------------------------------------------------------
def on_press(event):
    if event.num == 3: return
    face_label._drag_start_x = event.x
    face_label._drag_start_y = event.y
    face_label._is_dragging = False

def on_drag(event):
    global history_win, bubble_win, toolbar_win
    dx, dy = abs(event.x - face_label._drag_start_x), abs(event.y - face_label._drag_start_y)
    if dx > 5 or dy > 5:
        if not getattr(face_label, '_is_dragging', False):
            if history_win: history_win.destroy(); history_win = None
            if bubble_win: bubble_win.destroy(); bubble_win = None
            if toolbar_win: toolbar_win.destroy(); toolbar_win = None
            face_label._is_dragging = True
            
        x, y = root.winfo_x() - face_label._drag_start_x + event.x, root.winfo_y() - face_label._drag_start_y + event.y
        root.geometry(f"+{x}+{y}")
        
        # 💡 [핵심] 로봇을 끌고 다닐 때 머리 위 타워들도 함께 졸졸 따라오게 만듭니다!
        bot.update_todo_position()
        if hasattr(bot, 'update_folder_position'): bot.update_folder_position() 
        if hasattr(bot, 'update_stock_position'): bot.update_stock_position()

def fetch_news_loop():
    time.sleep(2)
    while True:
        bot.check_alarm()
        settings = get_settings()
        limit, duration, interval_seconds, custom_kw = settings["news_count"], settings["bubble_duration"], settings["alarm_interval"], settings["custom_keyword"]

        try: hourly_news = get_news_from_db(30, custom_kw)
        except: hourly_news = []

        if len(hourly_news) > 0:
            briefing_count = limit if limit > 0 and limit <= 10 else 10
            sample_count = min(len(hourly_news), briefing_count)
            briefing_news = random.sample(hourly_news, sample_count)
            root.after(0, lambda: play_bubble_sequence(briefing_news, 0, duration))
        
        for _ in range(int(interval_seconds / 5)): time.sleep(5)

# ---------------------------------------------------------
# 윈도우 초기화 및 실행
# ---------------------------------------------------------
root = tk.Tk()
root.geometry("+1500+800") 
root.overrideredirect(True)
root.attributes("-topmost", True)
root.configure(bg='magenta')
root.attributes("-transparentcolor", "magenta")

face_label = tk.Label(root, text="🤖", font=("Arial", 45), bg="magenta", cursor="fleur")
face_label.pack()

bot = AssistantFeatures(root, face_label, show_bubble)

face_label.bind("<ButtonPress-1>", on_press)
face_label.bind("<B1-Motion>", on_drag)
face_label.bind("<ButtonRelease-1>", toggle_all_menus)

threading.Thread(target=fetch_news_loop, daemon=True).start()
root.mainloop()