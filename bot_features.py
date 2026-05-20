import tkinter as tk
import datetime
import sqlite3
import os
import threading
from tkinter import simpledialog
import tkinter.messagebox as messagebox
from PIL import ImageGrab
import base64
from io import BytesIO

import requests

# ---------------------------------------------------------
# ⛅ 잃어버린 날씨 엔진 (WeatherFeature) 복구!
# ---------------------------------------------------------
class WeatherFeature:
    WMO_MAP = {
        0: ("☀️", "맑음"), 1: ("🌤️", "대체로 맑음"), 2: ("⛅", "구름조금"), 3: ("☁️", "흐림"),
        45: ("🌫️", "안개"), 48: ("🌫️", "안개"),
        51: ("🌧️", "가벼운 이슬비"), 53: ("🌧️", "이슬비"), 55: ("🌧️", "강한 이슬비"),
        61: ("☔", "가벼운 비"), 63: ("☔", "비"), 65: ("☔", "강한 비"),
        71: ("❄️", "가벼운 눈"), 73: ("❄️", "눈"), 75: ("❄️", "강한 눈"),
        95: ("⛈️", "천둥번개")
    }

    @staticmethod
    def get_weather_briefing(location="서울"):
        try:
            url = "https://api.open-meteo.com/v1/forecast?latitude=37.566&longitude=126.978&current_weather=true&hourly=temperature_2m,precipitation_probability,weathercode&timezone=Asia%2FSeoul"
            data = requests.get(url, timeout=5).json()
            
            cur = data.get("current_weather", {})
            cur_temp = cur.get("temperature", 0)
            cur_code = cur.get("weathercode", 0)
            
            from datetime import datetime
            now_hour = datetime.now().hour
            hours = data["hourly"]["time"]
            temps = data["hourly"]["temperature_2m"]
            codes = data["hourly"]["weathercode"]
            rains = data["hourly"]["precipitation_probability"]
            
            # 현재 시간의 강수 확률 찾기
            cur_rain = 0
            for i, t in enumerate(hours):
                if int(t[11:13]) == now_hour:
                    cur_rain = rains[i]
                    break
                    
            icon, status = WeatherFeature.WMO_MAP.get(cur_code, ("⛅", "알 수 없음"))
            briefing_text = f"🌡 현재 {location}: {status} {cur_temp}°C (강수 {cur_rain}%)\n\n"
            will_rain = cur_rain >= 40 or "비" in status or "눈" in status or "소나기" in status
            
            count = 0
            for i, t in enumerate(hours):
                h = int(t[11:13])
                if h <= now_hour: continue
                
                wicon, wstatus = WeatherFeature.WMO_MAP.get(codes[i], ("⛅", "?"))
                briefing_text += f"▪ {h}시: {round(temps[i])}°C {wicon} {wstatus} (강수 {rains[i]}%)\n"
                
                if rains[i] >= 40 or "비" in wstatus or "눈" in wstatus:
                    will_rain = True
                
                count += 1
                if count >= 6: break

            if will_rain:
                icon = "☔"
                briefing_text += "\n💡 비/눈 올 가능성 있어요! 우산 챙기세요!"
                
            return icon, briefing_text
        except Exception as e:
            return "⛅", "날씨 정보를 불러오지 못했습니다."

# =========================================================
# 이 아래부터는 원래 있던 class AssistantFeatures: 가 이어집니다!
# =========================================================
# 💡 주식 자동 갱신 주기 (초) — 여기서 바꾸세요!
STOCK_REFRESH_SECONDS = 30

class AssistantFeatures:
    def __init__(self, root, face_label, show_bubble_func):
        self.root = root
        self.face_label = face_label
        self.show_bubble = show_bubble_func
        
        self.timer_seconds = 0
        self.is_timer_running = False
        self.target_alarm_time = ""
        
        self.todo_win = None
        self.folder_win = None
        self.stock_win = None
        
        self._stock_refresh_id = None
        self.overlay = None
        self.start_x = 0
        self.start_y = 0
        self.rect = None

        # ---------------------------------------------------------
        # ⛅ 날씨 아이콘 세팅
        # ---------------------------------------------------------
        self.weather_label = tk.Label(
            self.root, 
            text="⛅", 
            font=("Segoe UI Emoji", 14), 
            bg="magenta", 
            fg="black",
            cursor="hand2"
        )
        self.face_label.pack_forget()
        self.weather_label.pack(side="top", pady=(0, 0))
        self.face_label.pack(side="bottom")
        
        self.weather_label.bind("<Button-1>", self.on_weather_click)
        self.current_weather_briefing = "날씨 정보를 불러오는 중입니다..."
        self.update_weather()


    def on_weather_click(self, event):
        display_time_ms = 20000 
        self.show_bubble(self.current_weather_briefing, "WEATHER", display_time_ms, True)    
    
    def update_weather(self):
        def fetch():
            icon, briefing = WeatherFeature.get_weather_briefing("서울")
            self.current_weather_briefing = briefing
            self.root.after(0, lambda: self.weather_label.config(text=icon))
            self.root.after(1800000, self.update_weather)
        threading.Thread(target=fetch, daemon=True).start()

    # ---------------------------------------------------------
    # ⏳ 타이머 및 알람
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
    # 📅 할 일 타워 기능 (다크모드 패널 적용)
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
        except Exception:
            return []

    def toggle_todo_bubbles(self):
        if self.todo_win and self.todo_win.winfo_exists():
            self.todo_win.destroy()
            self.todo_win = None
        else:
            self.draw_todo_bubbles()

    def draw_todo_bubbles(self):
        if self.todo_win and self.todo_win.winfo_exists():
            self.todo_win.destroy()
        items = self.get_today_schedules()
        if not items:
            self.show_bubble("오늘 등록된 일정이 없습니다! ☕", "ALARM", 3000, True)
            return

        self.todo_win = tk.Toplevel(self.root)
        self.todo_win.overrideredirect(True)
        self.todo_win.attributes("-topmost", True)
        self.todo_win.configure(bg='#202124')

        container = tk.Frame(self.todo_win, bg='#202124', padx=15, pady=15, relief="ridge", bd=2)
        container.pack()

        tk.Label(container, text="📅 오늘 할 일", bg='#202124', fg="white", font=("맑은 고딕", 10, "bold")).pack(side="top", pady=(0, 10))

        def mark_done(event, lbl):
            if lbl.cget("bg") != "#1a73e8":
                lbl.config(bg="#1a73e8", fg="white", text=lbl.cget("text") + " (✔완료)")

        for item in reversed(items):
            lbl = tk.Label(container, text=f"📌 {item['content']}", bg="#3c4043", fg="white", font=("맑은 고딕", 10), relief="flat", padx=12, pady=6, cursor="hand2", anchor="w")
            lbl.pack(side="bottom", pady=2, fill="x")
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
    # 📸 스크린샷 & 클립보드 복사
    # ---------------------------------------------------------
    def _get_dpi_scale(self):
        try:
            import ctypes
            hwnd = self.root.winfo_id()
            dpi = ctypes.windll.user32.GetDpiForWindow(hwnd)
            return dpi / 96.0
        except Exception:
            return 1.0

    def start_screenshot(self):
        self.overlay = tk.Toplevel(self.root)
        self.overlay.attributes("-topmost", True)
        self.overlay.attributes("-alpha", 0.3)
        self.overlay.configure(bg="black")
        
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.overlay.geometry(f"{sw}x{sh}+0+0")
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
        self.start_x = event.x_root
        self.start_y = event.y_root
        self.rect = self.canvas.create_rectangle(event.x, event.y, event.x, event.y, outline="red", width=2, fill="")

    def on_screen_drag(self, event):
        self.canvas.coords(self.rect, self.start_x - self.overlay.winfo_rootx(), self.start_y - self.overlay.winfo_rooty(), event.x, event.y)

    def on_screen_release(self, event):
        end_x = event.x_root
        end_y = event.y_root
        self.overlay.destroy()
        
        if abs(end_x - self.start_x) < 10 or abs(end_y - self.start_y) < 10:
            self.show_bubble("영역이 너무 작아 캡처가 취소되었습니다.", "ALARM", 2000, True)
            return
            
        self.root.after(200, lambda: self._capture_and_copy(self.start_x, self.start_y, end_x, end_y))

    def _capture_and_copy(self, x1, y1, x2, y2):
        try:
            import mss 
            from PIL import Image
            import win32clipboard
            from io import BytesIO
            import requests
            import base64
        except ImportError:
            self.show_bubble("📸 [오류]\n터미널에서 mss, pillow를 설치해주세요!", "ALARM", 5000, True)
            return

        left = min(x1, x2)
        top = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        
        monitor = {"top": top, "left": left, "width": width, "height": height}

        with mss.mss() as sct:
            sct_img = sct.grab(monitor)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

        import datetime, os
        save_dir = "screenshots"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
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
                self.show_bubble("📸 찰칵!\n클립보드, 파일, 서버에 모두 저장됨!", "ALARM", 4000, True)
            else:
                self.show_bubble(f"📸 찰칵!\nDB 저장 실패: {response.status_code}", "ALARM", 4000, True)
        except Exception:
            self.show_bubble("📸 찰칵!\n서버가 꺼져있거나 오류가 났습니다.", "ALARM", 4000, True)

    # ---------------------------------------------------------
    # 🚀 퀵 폴더 기능 (다크모드 패널 적용)
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
        except Exception:
            return []

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
        self.folder_win.configure(bg='#202124')

        container = tk.Frame(self.folder_win, bg='#202124', padx=15, pady=15, relief="ridge", bd=2)
        container.pack()

        tk.Label(container, text="📁 퀵 폴더", bg='#202124', fg="white", font=("맑은 고딕", 10, "bold")).pack(side="top", pady=(0, 10))

        items = self.get_quick_folders()

        def open_folder(path):
            try:
                os.startfile(path)
            except Exception:
                self.show_bubble("❌ 경로를 열 수 없습니다.\n경로가 올바른지 확인해주세요.", "ALARM", 3000, True)

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
            except Exception: pass

        add_btn = tk.Label(container, text="➕ 새 폴더 등록", bg="#fbbc05", fg="black", font=("맑은 고딕", 9, "bold"), relief="flat", padx=15, pady=6, cursor="hand2")
        add_btn.pack(side="bottom", pady=(10, 0), fill="x")
        add_btn.bind("<Button-1>", lambda e: add_new_folder())

        for item in reversed(items):
            frame = tk.Frame(container, bg='#202124')
            frame.pack(side="bottom", pady=2, fill="x")

            lbl = tk.Label(frame, text=f" {item['name']}", bg="#3c4043", fg="white", font=("맑은 고딕", 10), relief="flat", padx=12, pady=6, cursor="hand2", anchor="w")
            lbl.pack(side="left", fill="x", expand=True)
            lbl.bind("<Button-1>", lambda e, p=item['path']: open_folder(p))

            del_btn = tk.Label(frame, text="✖", bg="#ea4335", fg="white", font=("Arial", 8, "bold"), relief="flat", padx=8, pady=6, cursor="hand2")
            del_btn.pack(side="right", padx=(2, 0))
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
    # 📈 주식 전광판 타워 기능 (다크모드 패널 적용)
    # ---------------------------------------------------------
    def get_favorite_stocks_from_db(self):
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
        if not hasattr(self, 'stock_win'):
            self.stock_win = None

        if self.stock_win and self.stock_win.winfo_exists():
            if self._stock_refresh_id:
                self.root.after_cancel(self._stock_refresh_id)
                self._stock_refresh_id = None
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
        self.stock_win.configure(bg='#202124')

        container = tk.Frame(self.stock_win, bg='#202124', padx=15, pady=15, relief="ridge", bd=2)
        container.pack()

        tk.Label(container, text="📈 관심 주식", bg='#202124', fg="white", font=("맑은 고딕", 10, "bold")).pack(side="top", pady=(0, 10))

        loading_lbl = tk.Label(
            container, text="📡 불러오는 중...",
            bg="#3c4043", fg="white", font=("맑은 고딕", 9),
            relief="flat", padx=10, pady=5
        )
        loading_lbl.pack(side="bottom", pady=2, fill="x")

        self.stock_win.update_idletasks()
        self.update_stock_position()

        def fetch_stocks():
            import requests
            stocks = self.get_favorite_stocks_from_db()

            if not stocks:
                self.root.after(0, render_empty)
                return

            results = []
            for stock in stocks:
                try:
                    res = requests.get(f"http://localhost:8000/api/stock/{stock['ticker']}", timeout=10).json()
                    results.append({"name": stock["name"], "data": res})
                except Exception:
                    results.append({"name": stock["name"], "data": {"status": "error"}})

            self.root.after(0, lambda: render_stocks(results))

        def render_empty():
            if not self.stock_win or not self.stock_win.winfo_exists(): return
            loading_lbl.destroy()
            tk.Label(
                container, text="등록된 종목이 없습니다",
                bg="#3c4043", fg="#b0b0b0", font=("맑은 고딕", 10),
                relief="flat", padx=12, pady=6
            ).pack(side="bottom", pady=2, fill="x")
            self.stock_win.update_idletasks()
            self.update_stock_position()

        def render_stocks(results):
            if not self.stock_win or not self.stock_win.winfo_exists(): return
            loading_lbl.destroy()

            for item in reversed(results):
                name = item["name"]
                data = item["data"]

                if data.get("status") == "success":
                    price = data["price"]
                    diff  = data["diff"]
                    pct   = data["diff_percent"]

                    if diff > 0:
                        bg_color, fg_color, arrow = "#fce8e6", "#d93025", "🔺"
                    elif diff < 0:
                        bg_color, fg_color, arrow = "#e8f0fe", "#1a73e8", "🔻"
                    else:
                        bg_color, fg_color, arrow = "#f1f3f4", "black", "➖"

                    text = f"{name} : {price:,.2f} ({arrow} {abs(pct)}%)"
                else:
                    bg_color, fg_color, text = "#3c4043", "#b0b0b0", f"{name} : 정보 없음"

                lbl = tk.Label(
                    container, text=text,
                    bg=bg_color, fg=fg_color,
                    font=("맑은 고딕", 10, "bold"),
                    relief="flat", padx=12, pady=6, anchor="w",
                    cursor="hand2"
                )
                lbl.pack(side="bottom", pady=2, fill="x")
                lbl.bind("<Button-1>", lambda e, n=name: self.on_stock_click(n))

            self.stock_win.update_idletasks()
            self.update_stock_position()

            if self.stock_win and self.stock_win.winfo_exists():
                self._stock_refresh_id = self.root.after(STOCK_REFRESH_SECONDS * 1000, self.draw_stock_bubbles)

        threading.Thread(target=fetch_stocks, daemon=True).start()

    def update_stock_position(self):
        if hasattr(self, 'stock_win') and self.stock_win and self.stock_win.winfo_exists():
            rx, ry, rw = self.root.winfo_x(), self.root.winfo_y(), self.root.winfo_width()
            tw, th = self.stock_win.winfo_reqwidth(), self.stock_win.winfo_reqheight()
            tx = rx + (rw // 2) - (tw // 2)
            ty = ry - th - 5
            self.stock_win.geometry(f"+{tx}+{ty}")

    # ---------------------------------------------------------
    # 💡 [수정] 주식 전광판 클릭 시 리액트 웹으로 검색어 쏴버리기!
    # ---------------------------------------------------------
    def on_stock_click(self, stock_name):
        import urllib.parse
        import webbrowser
        
        safe_name = urllib.parse.quote(stock_name)
        PORT = 5173 
        target_url = f"http://localhost:{PORT}/?search={safe_name}"
        webbrowser.open(target_url)

    # ---------------------------------------------------------
    # 🧭 [가이드 모드 & 진행판 HUD] 부품 추가
    # ---------------------------------------------------------
    # ---------------------------------------------------------
    # 🧭 [가이드 모드 & 진행판 HUD] 부품 추가
    # ---------------------------------------------------------
    def start_guide_mode(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("가이드 대본 입력")
        dialog.attributes("-topmost", True)
        dialog.configure(bg="#202124")
        
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        w, h = sw // 2, sh // 2
        dialog.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        
        tk.Label(dialog, text="📝 대본을 입력하세요. (엔터 3번으로 단계 구분)", font=("맑은 고딕", 12, "bold"), bg="#202124", fg="white").pack(pady=10)
        
        input_area = tk.Text(dialog, font=("맑은 고딕", 11), wrap="word", bg="#3c4043", fg="white", insertbackground="white")
        input_area.pack(fill="both", expand=True, padx=15, pady=5)
        
        guide_text = ""
        def on_submit():
            nonlocal guide_text
            guide_text = input_area.get("1.0", "end-1c")
            dialog.destroy()
            
        tk.Button(dialog, text="✅ 확인 (대본 입력 완료)", command=on_submit, bg="#4CAF50", fg="white", font=("맑은 고딕", 12, "bold"), padx=20).pack(pady=10)
        
        dialog.grab_set()
        self.root.wait_window(dialog)
        
        if not guide_text.strip(): return
        
        steps = [s.strip() for s in guide_text.split('\n\n\n') if s.strip()]
        if not steps: return
        self.current_guide_step = 0
        
        # 2. 💡 [수정] 로봇 '왼쪽 옆구리'를 따라다니는 진행판! (뉴스와 겹침 방지)
        hud = tk.Toplevel(self.root)
        hud.overrideredirect(True)
        hud.attributes("-topmost", True)
        hud.configure(bg="#2b2b2b")
        
        def follow_robot():
            if hud.winfo_exists():
                rx, ry, rw = self.root.winfo_x(), self.root.winfo_y(), self.root.winfo_width()
                hw, hh = hud.winfo_reqwidth(), hud.winfo_reqheight()
                
                # 💡 X좌표를 로봇 몸통 너비만큼 왼쪽으로 뺍니다!
                tx = rx - hw - 15
                ty = ry + (rw // 2) - (hh // 2)
                
                hud.geometry(f"+{tx}+{ty}")
                hud.after(20, follow_robot)
        follow_robot()
        
        # 단계 헤더
        step_header = tk.Label(hud, text="", font=("맑은 고딕", 10, "bold"),
                               fg="#fbbc05", bg="#2b2b2b")
        step_header.pack(pady=(8, 4))

        # 단어 버튼 영역
        word_frame = tk.Frame(hud, bg="#2b2b2b")
        word_frame.pack(padx=10, pady=(0, 6), fill="x")

        def clear_word_buttons():
            for w in word_frame.winfo_children():
                w.destroy()

        # 선택된 단어 버튼 목록
        selected_btns = []
        selected_words = []

        def search_selected():
            """선택된 단어들을 공백으로 합쳐서 OCR 검색"""
            if not selected_words:
                return
            query = " ".join(selected_words)
            self.start_tracking_target_by_word(query)

        # 검색 버튼 (단어 버튼 위에 배치)
        search_bar = tk.Frame(hud, bg="#2b2b2b")
        search_bar.pack(fill="x", padx=10, pady=(0, 4))

        selected_label = tk.Label(search_bar, text="선택: 없음",
                                  font=("맑은 고딕", 8), fg="#aaaaaa", bg="#2b2b2b")
        selected_label.pack(side="left", expand=True, anchor="w")

        tk.Button(search_bar, text="🔍 검색", font=("맑은 고딕", 9, "bold"),
                  bg="#1a73e8", fg="white", relief="flat", cursor="hand2",
                  padx=8, pady=2, command=search_selected).pack(side="right", padx=(4,0))

        tk.Button(search_bar, text="✖ 초기화", font=("맑은 고딕", 9),
                  bg="#5f6368", fg="white", relief="flat", cursor="hand2",
                  padx=6, pady=2,
                  command=lambda: clear_selection()).pack(side="right", padx=2)

        def clear_selection():
            for b in selected_btns:
                if b.winfo_exists():
                    b.config(bg="#3c4043", fg="white")
            selected_btns.clear()
            selected_words.clear()
            selected_label.config(text="선택: 없음")

        def build_word_buttons(text):
            """공백으로 단어 분리 → 다중 토글 버튼 생성"""
            clear_word_buttons()
            selected_btns.clear()
            selected_words.clear()
            selected_label.config(text="선택: 없음")

            words = text.split()
            row_frame = None
            for i, word in enumerate(words):
                if i % 6 == 0:
                    row_frame = tk.Frame(word_frame, bg="#2b2b2b")
                    row_frame.pack(anchor="w", pady=1)
                btn = tk.Button(
                    row_frame, text=word,
                    font=("맑은 고딕", 9, "bold"),
                    bg="#3c4043", fg="white",
                    relief="flat", cursor="hand2",
                    padx=6, pady=3
                )
                btn.pack(side="left", padx=2)

                def on_click(b=btn, w=word):
                    if b in selected_btns:
                        # 선택 해제
                        b.config(bg="#3c4043", fg="white")
                        selected_btns.remove(b)
                        selected_words.remove(w)
                    else:
                        # 선택 추가
                        b.config(bg="#e91e63", fg="white")
                        selected_btns.append(b)
                        selected_words.append(w)

                    if selected_words:
                        selected_label.config(text=f"선택: {' '.join(selected_words)}")
                    else:
                        selected_label.config(text="선택: 없음")

                btn.config(command=on_click)

        def update_hud():
            if self.current_guide_step >= len(steps):
                clear_word_buttons()
                step_header.config(text="✅ 가이드 완료!")
                btn_next.config(state="disabled")
                hud.after(3000, hud.destroy)
                return
            current_idx = self.current_guide_step
            step_header.config(text=f"[{current_idx + 1} / {len(steps)}]")
            build_word_buttons(steps[current_idx])

        def next_step():
            self.current_guide_step += 1
            if hasattr(self, 'active_tracking_boxes'):
                for box in self.active_tracking_boxes:
                    if box.winfo_exists():
                        box.destroy()
                self.active_tracking_boxes.clear()
            update_hud()
            
        def report_error():
            hud.withdraw()
            self.root.update()
            import time
            time.sleep(0.3)
            
            try:
                import base64
                from io import BytesIO
                from PIL import ImageGrab
                import sqlite3
                import tkinter.messagebox as messagebox
                
                img = ImageGrab.grab()
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                img_b64 = "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode()
                error_msg = f"🚨 [오류 발생 단계] {steps[self.current_guide_step]}"
                
                import requests as _req
                _req.post("http://localhost:8000/api/clipboard", json={"type": "text", "content": error_msg})
                _req.post("http://localhost:8000/api/clipboard", json={"type": "image", "content": img_b64})
                messagebox.showinfo("오류 캡처 완료", "리액트 클립보드에 자동 저장되었습니다!")
            except Exception as e:
                pass
                
            hud.deiconify()
            
        btn_frame = tk.Frame(hud, bg="#2b2b2b")
        btn_frame.pack(side="bottom", pady=10)
        
        btn_next = tk.Button(btn_frame, text="▶ 다음", command=next_step, bg="#4CAF50", fg="white", font=("맑은 고딕", 10, "bold"))
        btn_next.pack(side="left", padx=5)
        
        btn_error = tk.Button(btn_frame, text="🚨 오류", command=report_error, bg="#f44336", fg="white", font=("맑은 고딕", 10, "bold"))
        btn_error.pack(side="left", padx=5)
        
        
        btn_close = tk.Button(btn_frame, text="✖ 종료", command=hud.destroy, bg="#5f6368", fg="white", font=("맑은 고딕", 10, "bold"))
        btn_close.pack(side="left", padx=5)
        
        update_hud()

    # ---------------------------------------------------------
    # 🎯 [신규] 실시간 타겟 추적 (채팅창 숫자 버그 완전 우회판!)
    # ---------------------------------------------------------
    def start_tracking_target_by_word(self, target_text):
        """단어 버튼 클릭 시 바로 OCR 검색"""
        self.show_bubble(f"\U0001f50d [{target_text}]\nWindows OCR \uc2a4\uce94 \uc911...", "ALARM", 2000, True)

        import threading, io, asyncio, time
        from PIL import ImageGrab

        def draw_red_box(x, y, w, h, rank):
            box_win = tk.Toplevel(self.root)
            if not hasattr(self, 'active_tracking_boxes'):
                self.active_tracking_boxes = []
            self.active_tracking_boxes.append(box_win)
            box_win.overrideredirect(True)
            box_win.attributes("-topmost", True)
            box_win.attributes("-transparentcolor", "white")
            pad = 5
            box_win.geometry(f"{w+pad*2}x{h+pad*2}+{x-pad}+{y-pad}")
            canvas = tk.Canvas(box_win, bg="white", highlightthickness=0)
            canvas.pack(fill="both", expand=True)
            color = "red" if rank == 1 else "orange"
            lw = 5 if rank == 1 else 2
            canvas.create_rectangle(pad, pad, w+pad, h+pad, outline=color, width=lw)
            box_win.bind("<Button-1>", lambda e: box_win.destroy())
            canvas.bind("<Button-1>", lambda e: box_win.destroy())

        async def run_ocr(pil_img):
            from winrt.windows.media.ocr import OcrEngine
            from winrt.windows.graphics.imaging import BitmapDecoder
            from winrt.windows.storage.streams import InMemoryRandomAccessStream, DataWriter

            buf = io.BytesIO()
            pil_img.save(buf, format="PNG")
            img_bytes = buf.getvalue()

            lang = None
            try:
                for l in OcrEngine.get_available_recognizer_languages():
                    if "ko" in l.language_tag.lower():
                        lang = l
                        break
            except Exception:
                pass

            try:
                engine = (OcrEngine.try_create_from_language(lang)
                          if lang else OcrEngine.try_create_from_user_profile_languages())
            except Exception:
                engine = OcrEngine.try_create_from_user_profile_languages()

            if engine is None:
                return []

            stream = InMemoryRandomAccessStream()
            writer = DataWriter(stream)
            writer.write_bytes(img_bytes)
            await writer.store_async()
            writer.detach_stream()
            stream.seek(0)

            decoder = await BitmapDecoder.create_async(stream)
            bitmap = await decoder.get_software_bitmap_async()
            result = await engine.recognize_async(bitmap)

            words = []
            for line in result.lines:
                for word in line.words:
                    r = word.bounding_rect
                    words.append({"text": word.text,
                                  "x": int(r.x), "y": int(r.y),
                                  "w": int(r.width), "h": int(r.height)})
            return words

        def loop():
            while True:
                screen_img = ImageGrab.grab()
                try:
                    ev_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(ev_loop)
                    words = ev_loop.run_until_complete(run_ocr(screen_img))
                    ev_loop.close()
                except Exception as e:
                    self.root.after(0, lambda err=str(e): self.show_bubble(
                        f"\u274c OCR \uc624\ub958\n{err[:50]}", "ALARM", 3000, True))
                    return

                found = []
                seen = set()
                for word in words:
                    wt = word["text"]
                    if target_text in wt or wt in target_text:
                        pos_key = (word["x"] // 50, word["y"] // 50)
                        if pos_key in seen:
                            continue
                        seen.add(pos_key)
                        found.append(word)

                if found:
                    for i, word in enumerate(found[:3]):
                        x, y, w, h = word["x"], word["y"], word["w"], word["h"]
                        self.root.after(0, lambda a=x, b=y, c=w, d=h, r=i+1:
                                        draw_red_box(a, b, c, d, r))
                        if i == 0:
                            self.root.after(0, lambda wd=word["text"]:
                                self.show_bubble(
                                    f"\U0001f3af [{wd}] \ubc1c\uacac!",
                                    "ALARM", 3000, True))
                    break
                else:
                    self.root.after(0, lambda: self.show_bubble(
                        f"\U0001f605 [{target_text}] \ubabb \ucc3e\uc74c\n\ub2e4\uc2dc \uc2dc\ub3c4...",
                        "ALARM", 2000, True))
                    time.sleep(1)

        threading.Thread(target=loop, daemon=True).start()

    def start_tracking_target(self, text_widget):
        try:
            target_text = text_widget.get(tk.SEL_FIRST, tk.SEL_LAST).strip()
        except tk.TclError:
            self.show_bubble("찾을 글자를 먼저 마우스로 긁어주세요!", "ALARM", 3000, True)
            return

        if not target_text: return
        self.show_bubble(f"\U0001f50d [{target_text}]\nWindows OCR 스캔 중...", "ALARM", 2000, True)

        import threading

        def draw_red_box(x, y, w, h, rank):
            box_win = tk.Toplevel(self.root)
            if not hasattr(self, 'active_tracking_boxes'):
                self.active_tracking_boxes = []
            self.active_tracking_boxes.append(box_win)
            box_win.overrideredirect(True)
            box_win.attributes("-topmost", True)
            box_win.attributes("-transparentcolor", "white")
            pad = 5
            box_win.geometry(f"{w + pad*2}x{h + pad*2}+{x - pad}+{y - pad}")
            canvas = tk.Canvas(box_win, bg="white", highlightthickness=0)
            canvas.pack(fill="both", expand=True)
            color = "red" if rank == 1 else "orange"
            lw = 5 if rank == 1 else 2
            canvas.create_rectangle(pad, pad, w + pad, h + pad, outline=color, width=lw)
            box_win.bind("<Button-1>", lambda e: box_win.destroy())
            canvas.bind("<Button-1>", lambda e: box_win.destroy())

        def tracking_loop():
            import asyncio, time, io
            from PIL import ImageGrab

            async def run_ocr(pil_img):
                from winrt.windows.media.ocr import OcrEngine
                from winrt.windows.graphics.imaging import BitmapDecoder
                from winrt.windows.storage.streams import (
                    InMemoryRandomAccessStream, DataWriter)

                # PIL → PNG bytes
                buf = io.BytesIO()
                pil_img.save(buf, format="PNG")
                img_bytes = buf.getvalue()

                # 한국어 엔진 우선
                lang = None
                try:
                    for l in OcrEngine.get_available_recognizer_languages():
                        if "ko" in l.language_tag.lower():
                            lang = l
                            break
                except Exception:
                    pass

                try:
                    engine = (OcrEngine.try_create_from_language(lang)
                              if lang else
                              OcrEngine.try_create_from_user_profile_languages())
                except Exception:
                    engine = OcrEngine.try_create_from_user_profile_languages()

                if engine is None:
                    return []

                # bytes → stream → bitmap
                stream = InMemoryRandomAccessStream()
                writer = DataWriter(stream)
                writer.write_bytes(img_bytes)
                await writer.store_async()
                writer.detach_stream()
                stream.seek(0)

                decoder = await BitmapDecoder.create_async(stream)
                bitmap = await decoder.get_software_bitmap_async()

                result = await engine.recognize_async(bitmap)

                words = []
                for line in result.lines:
                    for word in line.words:
                        r = word.bounding_rect
                        words.append({
                            "text": word.text,
                            "x": int(r.x), "y": int(r.y),
                            "w": int(r.width), "h": int(r.height),
                        })
                return words

            while True:
                screen_img = ImageGrab.grab()
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    words = loop.run_until_complete(run_ocr(screen_img))
                    loop.close()
                except Exception as e:
                    self.root.after(0, lambda err=str(e): self.show_bubble(
                        f"\u274c OCR \uc624\ub958\n{err[:50]}", "ALARM", 3000, True))
                    return

                found = []
                seen = set()
                for word in words:
                    wt = word["text"]
                    if target_text in wt or wt in target_text:
                        pos_key = (word["x"] // 50, word["y"] // 50)
                        if pos_key in seen:
                            continue
                        seen.add(pos_key)
                        found.append(word)

                if found:
                    for i, word in enumerate(found[:3]):
                        x, y, w, h = word["x"], word["y"], word["w"], word["h"]
                        self.root.after(0, lambda a=x, b=y, c=w, d=h, r=i+1:
                                        draw_red_box(a, b, c, d, r))
                        if i == 0:
                            self.root.after(0, lambda wd=word["text"]:
                                self.show_bubble(
                                    f"\U0001f3af \ubc1c\uacac! [{wd}]\nWindows OCR \uc131\uacf5!",
                                    "ALARM", 3000, True))
                    break
                else:
                    self.root.after(0, lambda: self.show_bubble(
                        f"\U0001f605 [{target_text}] \ubabb \ucc3e\uc558\uc5b4\uc694\n\ub2e4\uc2dc \uc2dc\ub3c4 \uc911...",
                        "ALARM", 2000, True))
                    time.sleep(1)

        threading.Thread(target=tracking_loop, daemon=True).start()