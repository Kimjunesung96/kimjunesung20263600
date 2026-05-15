import tkinter as tk
import datetime
import sqlite3
import os
from tkinter import simpledialog
import tkinter.messagebox as messagebox

class AssistantFeatures:
    def __init__(self, root, face_label, show_bubble_func):
        self.root = root
        self.face_label = face_label
        self.show_bubble = show_bubble_func
        
        # 타이머 및 알람 상태
        self.timer_seconds = 0
        self.is_timer_running = False
        self.target_alarm_time = ""
        
        # 윈도우 창 변수들
        self.todo_win = None
        self.folder_win = None
        self.stock_win = None
        
        # 스샷용 변수
        self.overlay = None
        self.start_x = 0
        self.start_y = 0
        self.rect = None

    # ---------------------------------------------------------
    # ⏳ 타이머
    # ---------------------------------------------------------
    def start_timer(self, minutes):
        self.timer_seconds = minutes * 60
        self.is_timer_running = True
        self.update_timer()

    def stop_timer(self):
        self.is_timer_running = False
        self.face_label.config(text="🤖", font=("Arial", 45))

    def update_timer(self):
        if self.timer_seconds > 0 and self.is_timer_running:
            mins, secs = divmod(self.timer_seconds, 60)
            self.face_label.config(text=f"⏳\n{mins:02d}:{secs:02d}", font=("Arial", 20, "bold"))
            self.timer_seconds -= 1
            self.root.after(1000, self.update_timer)
        elif self.is_timer_running and self.timer_seconds <= 0:
            self.is_timer_running = False
            self.face_label.config(text="🚨", font=("Arial", 45))
            self.show_giant_alert("⏳ 타이머 종료!", "지정하신 타이머 시간이 다 되었습니다!")

    # ---------------------------------------------------------
    # ⏰ 알람 기능
    # ---------------------------------------------------------
    def set_alarm(self):
        time_str = simpledialog.askstring("알람 설정", "알람 시간을 입력하세요\n(예: 08:30, 14:00)")
        if time_str:
            self.target_alarm_time = time_str.strip()
            self.show_bubble(f"오늘 {self.target_alarm_time}에 알람이 설정되었습니다!", "ALARM", 3000, True)

    def check_alarm(self):
        if self.target_alarm_time:
            now_str = datetime.datetime.now().strftime("%H:%M")
            if now_str == self.target_alarm_time:
                self.show_bubble("⏰ 띠링! 설정하신 알람 시간입니다!\n좋은 하루 보내세요!", "ALARM", 10000, False)
                self.target_alarm_time = "" 

    def show_giant_alert(self, title, message):
        alert_win = tk.Toplevel(self.root)
        alert_win.attributes("-topmost", True)
        alert_win.overrideredirect(True)
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        alert_win.geometry(f"{sw}x{sh}+0+0")
        alert_win.configure(bg="black")
        alert_win.attributes("-alpha", 0.85) 
        
        def click_to_reset(event):
            alert_win.destroy()
            self.face_label.config(text="🤖", font=("Arial", 45))
        alert_win.bind("<Button-1>", click_to_reset)

        frame = tk.Frame(alert_win, bg="#ffeb3b", bd=10, relief="ridge", padx=50, pady=50)
        frame.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(frame, text=title, font=("맑은 고딕", 60, "bold"), bg="#ffeb3b", fg="#d32f2f").pack(pady=(0, 20))
        tk.Label(frame, text=message, font=("맑은 고딕", 25, "bold"), bg="#ffeb3b", fg="black").pack(pady=(0, 40))
        tk.Label(frame, text="(🚨 한번 클릭하면 원상태로 복귀합니다)", font=("맑은 고딕", 12, "bold"), bg="#ffeb3b", fg="#5f6368").pack()

    # ---------------------------------------------------------
    # 📅 할 일 타워 기능 
    # ---------------------------------------------------------
    def get_today_schedules(self):
        try:
            conn = sqlite3.connect('news.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            today_str = datetime.datetime.now().strftime("%Y-%m-%d")
            cursor.execute("SELECT id, content FROM schedule WHERE date = ? ORDER BY id ASC", (today_str,))
            rows = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return rows
        except Exception: return []

    def toggle_todo_bubbles(self):
        if self.todo_win and self.todo_win.winfo_exists():
            self.todo_win.destroy()
            self.todo_win = None
        else:
            self.draw_todo_bubbles()

    def draw_todo_bubbles(self):
        if self.todo_win and self.todo_win.winfo_exists(): self.todo_win.destroy()
        items = self.get_today_schedules()
        if not items:
            self.show_bubble("오늘 등록된 일정이 없습니다! ☕", "ALARM", 3000, True)
            return

        self.todo_win = tk.Toplevel(self.root)
        self.todo_win.overrideredirect(True)
        self.todo_win.attributes("-topmost", True)
        self.todo_win.configure(bg='magenta')
        self.todo_win.attributes("-transparentcolor", "magenta")

        def mark_done(event, lbl):
            if lbl.cget("bg") != "#1a73e8":
                lbl.config(bg="#1a73e8", fg="white", text=lbl.cget("text") + " (✔완료)")

        for item in reversed(items):
            lbl = tk.Label(self.todo_win, text=f"📌 {item['content']}", bg="#4caf50", fg="white", font=("맑은 고딕", 10, "bold"), relief="solid", bd=2, padx=12, pady=6, cursor="hand2")
            lbl.pack(side="bottom", pady=2)
            lbl.bind("<Button-1>", lambda e, l=lbl: mark_done(e, l))

        self.todo_win.update_idletasks()
        self.update_todo_position()

    def update_todo_position(self):
        if self.todo_win and self.todo_win.winfo_exists():
            rx, ry, rw = self.root.winfo_x(), self.root.winfo_y(), self.root.winfo_width()
            tw, th = self.todo_win.winfo_reqwidth(), self.todo_win.winfo_reqheight()
            tx = rx + (rw // 2) - (tw // 2)
            ty = ry - th - 5
            self.todo_win.geometry(f"+{tx}+{ty}")

    # ---------------------------------------------------------
    # 📸 스크린샷 & 클립보드 복사 기능
    # ---------------------------------------------------------
    def start_screenshot(self):
        self.overlay = tk.Toplevel(self.root)
        self.overlay.attributes("-topmost", True)
        self.overlay.attributes("-alpha", 0.3)
        self.overlay.configure(bg="black")
        self.overlay.attributes("-fullscreen", True)
        self.overlay.config(cursor="cross") 

        self.canvas = tk.Canvas(self.overlay, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.rect = None
        self.start_x = 0
        self.start_y = 0

        self.canvas.bind("<ButtonPress-1>", self.on_screen_press)
        self.canvas.bind("<B1-Motion>", self.on_screen_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_screen_release)
        self.overlay.bind("<Escape>", lambda e: self.overlay.destroy())

    def on_screen_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red", width=2, fill="white")

    def on_screen_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_screen_release(self, event):
        end_x, end_y = event.x, event.y
        self.overlay.destroy() 
        if abs(end_x - self.start_x) < 10 or abs(end_y - self.start_y) < 10:
            self.show_bubble("영역이 너무 작아 캡처가 취소되었습니다.", "ALARM", 2000, True)
            return
        self.root.after(200, lambda: self._capture_and_copy(self.start_x, self.start_y, end_x, end_y))

    def _capture_and_copy(self, x1, y1, x2, y2):
        try:
            from PIL import ImageGrab
            import win32clipboard
            from io import BytesIO
            import requests 
            import base64   
        except ImportError:
            self.show_bubble("📸 [오류]\n터미널에서 부품을 마저 설치해주세요!\npip install requests", "ALARM", 5000, True)
            return

        bbox = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
        img = ImageGrab.grab(bbox)
        
        save_dir = "screenshots"
        if not os.path.exists(save_dir): os.makedirs(save_dir)
        filename = f"capture_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(save_dir, filename)
        img.save(filepath, "PNG")

        output = BytesIO()
        img.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:] 
        output.close()
        
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()
        
        try:
            img_buffer = BytesIO()
            img.save(img_buffer, format="PNG")
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode("utf-8")
            base64_str = f"data:image/png;base64,{img_base64}"
            
            response = requests.post("http://localhost:8000/api/clipboard", json={"type": "image", "content": base64_str})
            if response.status_code == 200:
                self.show_bubble(f"📸 찰칵!\n클립보드, 파일, 서버에 모두 저장됨!", "ALARM", 4000, True)
            else:
                self.show_bubble(f"📸 찰칵!\nDB 저장 실패: {response.status_code}", "ALARM", 4000, True)
        except Exception as e:
            self.show_bubble(f"📸 찰칵!\n서버가 꺼져있거나 오류가 났습니다.", "ALARM", 4000, True)

    # ---------------------------------------------------------
    # 🚀 퀵 폴더 기능 (수동 등록)
    # ---------------------------------------------------------
    def get_quick_folders(self):
        try:
            conn = sqlite3.connect('news.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS quick_folders (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT, path TEXT)''')
            cursor.execute("SELECT id, name, path FROM quick_folders ORDER BY id ASC")
            rows = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return rows
        except Exception: return []

    def toggle_folder_bubbles(self):
        if self.folder_win and self.folder_win.winfo_exists():
            self.folder_win.destroy()
            self.folder_win = None
        else:
            self.draw_folder_bubbles()

    def draw_folder_bubbles(self):
        if hasattr(self, 'folder_win') and self.folder_win and self.folder_win.winfo_exists(): 
            self.folder_win.destroy()

        self.folder_win = tk.Toplevel(self.root)
        self.folder_win.overrideredirect(True)
        self.folder_win.attributes("-topmost", True)
        self.folder_win.configure(bg='magenta')
        self.folder_win.attributes("-transparentcolor", "magenta")

        items = self.get_quick_folders()

        def open_folder(path):
            import os
            try: os.startfile(path)
            except: self.show_bubble("❌ 경로를 열 수 없습니다.\n경로가 올바른지 확인해주세요.", "ALARM", 3000, True)

        def delete_folder(e, id):
            if messagebox.askyesno("삭제", "이 폴더를 즐겨찾기에서 지우시겠습니까?"):
                conn = sqlite3.connect('news.db')
                cursor = conn.cursor()
                cursor.execute("DELETE FROM quick_folders WHERE id=?", (id,))
                conn.commit()
                conn.close()
                self.draw_folder_bubbles()

        def add_new_folder():
            name = simpledialog.askstring("퀵 폴더 등록", "폴더의 별명을 입력하세요\n(예: 인공지능 과제)")
            if not name: return
            path = simpledialog.askstring("퀵 폴더 등록", "복사한 폴더 경로를 붙여넣으세요\n(예: C:\\Users\\... )")
            if not path: return
            
            try:
                conn = sqlite3.connect('news.db')
                cursor = conn.cursor()
                cursor.execute("INSERT INTO quick_folders (name, path) VALUES (?, ?)", (name, path))
                conn.commit()
                conn.close()
                self.draw_folder_bubbles()
            except: pass

        add_btn = tk.Label(self.folder_win, text="➕ 새 폴더 등록하기", bg="#fbbc05", fg="black", font=("맑은 고딕", 9, "bold"), relief="solid", bd=2, padx=15, pady=6, cursor="hand2")
        add_btn.pack(side="bottom", pady=4)
        add_btn.bind("<Button-1>", lambda e: add_new_folder())

        for item in reversed(items):
            frame = tk.Frame(self.folder_win, bg='magenta')
            frame.pack(side="bottom", pady=2)
            
            lbl = tk.Label(frame, text=f"📁 {item['name']}", bg="#8ab4f8", fg="black", font=("맑은 고딕", 10, "bold"), relief="solid", bd=2, padx=12, pady=6, cursor="hand2")
            lbl.pack(side="left")
            lbl.bind("<Button-1>", lambda e, p=item['path']: open_folder(p))
            
            del_btn = tk.Label(frame, text="✖", bg="#ea4335", fg="white", font=("Arial", 8, "bold"), relief="solid", bd=1, padx=4, pady=4, cursor="hand2")
            del_btn.pack(side="left", padx=(2,0))
            del_btn.bind("<Button-1>", lambda e, i=item['id']: delete_folder(e, i))

        self.folder_win.update_idletasks()
        self.update_folder_position()

    def update_folder_position(self):
        if hasattr(self, 'folder_win') and self.folder_win and self.folder_win.winfo_exists():
            rx, ry, rw = self.root.winfo_x(), self.root.winfo_y(), self.root.winfo_width()
            tw, th = self.folder_win.winfo_reqwidth(), self.folder_win.winfo_reqheight()
            tx = rx + (rw // 2) - (tw // 2)
            ty = ry - th - 5
            self.folder_win.geometry(f"+{tx}+{ty}")

    # ---------------------------------------------------------
    # 📈 주식 전광판 타워 기능
    # ---------------------------------------------------------

    def get_favorite_stocks_from_db(self):
        """💡 하드코딩 제거 - DB에서 실제 등록된 종목만 가져오기"""
        try:
            conn = sqlite3.connect('news.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT name, ticker FROM favorite_stocks ORDER BY id ASC")
            rows = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return rows
        except Exception:
            return []

    def toggle_stock_bubbles(self):
        if not hasattr(self, 'stock_win'): self.stock_win = None

        if self.stock_win and self.stock_win.winfo_exists():
            self.stock_win.destroy()
            self.stock_win = None
        else:
            self.draw_stock_bubbles()

    def draw_stock_bubbles(self):
        if hasattr(self, 'stock_win') and self.stock_win and self.stock_win.winfo_exists(): 
            self.stock_win.destroy()

        self.stock_win = tk.Toplevel(self.root)
        self.stock_win.overrideredirect(True)
        self.stock_win.attributes("-topmost", True)
        self.stock_win.configure(bg='magenta')
        self.stock_win.attributes("-transparentcolor", "magenta")

        loading_lbl = tk.Label(self.stock_win, text="📡 주식/코인 데이터 불러오는 중...", bg="#f1f3f4", fg="#5f6368", font=("맑은 고딕", 9, "bold"), relief="solid", bd=1, padx=10, pady=5)
        loading_lbl.pack(side="bottom", pady=2)
        
        self.stock_win.update_idletasks()
        self.update_stock_position()

        def fetch_stocks():
            import requests
            
            # ✅ 핵심 수정: 하드코딩 제거, DB에서 가져오기
            stocks = self.get_favorite_stocks_from_db()
            
            if not stocks:
                self.root.after(0, lambda: render_empty())
                return

            results = []
            for stock in stocks:
                try:
                    res = requests.get(f"http://localhost:8000/api/stock/{stock['ticker']}").json()
                    results.append({"name": stock["name"], "data": res})
                except:
                    results.append({"name": stock["name"], "data": {"status": "error"}})
            
            self.root.after(0, lambda: render_stocks(results))

        def render_empty():
            loading_lbl.destroy()
            lbl = tk.Label(self.stock_win, text="📈 등록된 종목이 없습니다", bg="#f1f3f4", fg="#5f6368", font=("맑은 고딕", 10, "bold"), relief="solid", bd=2, padx=12, pady=6)
            lbl.pack(side="bottom", pady=2)
            self.stock_win.update_idletasks()
            self.update_stock_position()

        def render_stocks(results):
            loading_lbl.destroy() 
            
            for item in reversed(results):
                name = item["name"]
                data = item["data"]
                
                if data.get("status") == "success":
                    price = data["price"]
                    diff = data["diff"]
                    pct = data["diff_percent"]
                    
                    if diff > 0:
                        bg_color, fg_color, arrow = "#fce8e6", "#d93025", "🔺"
                    elif diff < 0:
                        bg_color, fg_color, arrow = "#e8f0fe", "#1a73e8", "🔻"
                    else:
                        bg_color, fg_color, arrow = "white", "black", "➖"
                        
                    text = f"{name} : {price:,.2f} ({arrow} {abs(pct)}%)"
                else:
                    bg_color, fg_color, text = "#f1f3f4", "#5f6368", f"{name} : 정보 없음"

                lbl = tk.Label(self.stock_win, text=text, bg=bg_color, fg=fg_color, font=("맑은 고딕", 10, "bold"), relief="solid", bd=2, padx=12, pady=6)
                lbl.pack(side="bottom", pady=2)
            
            self.stock_win.update_idletasks()
            self.update_stock_position()

        import threading
        threading.Thread(target=fetch_stocks, daemon=True).start()

    def update_stock_position(self):
        if hasattr(self, 'stock_win') and self.stock_win and self.stock_win.winfo_exists():
            rx, ry, rw = self.root.winfo_x(), self.root.winfo_y(), self.root.winfo_width()
            tw, th = self.stock_win.winfo_reqwidth(), self.stock_win.winfo_reqheight()
            tx = rx + (rw // 2) - (tw // 2)
            ty = ry - th - 5
            self.stock_win.geometry(f"+{tx}+{ty}")