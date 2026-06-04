import tkinter as tk

class BubbleUI:
    def __init__(self, root, bot_ref):
        self.root = root
        self.bot = bot_ref
        self.bubble_win = None
        self.current_url = ""

    def show(self, title, url, duration_ms, auto_hide=True):
        """다양한 알림 유형에 맞는 말풍선을 화면에 표시합니다."""
        self.current_url = url
        
        if self.bubble_win and self.bubble_win.winfo_exists():
            self.bubble_win.destroy()
            
        self.bubble_win = tk.Toplevel(self.root)
        self.bubble_win.overrideredirect(True)
        self.bubble_win.attributes("-topmost", True)
        self.bubble_win.configure(bg='magenta')
        self.bubble_win.attributes("-transparentcolor", "magenta")
        
        # 유형별 테마 설정
        if url == "TIMER": 
            header_text, bg_color, fg_color = "⏳ [타이머 종료!]", "#ffeb3b", "#d32f2f"
        elif url == "ALARM": 
            header_text, bg_color, fg_color = "⏰ [알람 시간입니다!]", "#fce4ec", "#c2185b"
        elif url == "WEATHER": 
            header_text, bg_color, fg_color = "⛅ [오늘의 날씨 브리핑]", "#e0f7fa", "#006064"
        else: 
            header_text, bg_color, fg_color = "🔔 [최신 뉴스 브리핑!]", "#e8f0fe", "#1a73e8"

        short_title = title if url in ["ALARM", "TIMER", "WEATHER"] else (title[:30] + "..." if len(title) > 30 else title)

        lbl = tk.Label(self.bubble_win, text=f"{header_text}\n{short_title}", bg=bg_color, fg=fg_color, 
                       font=("맑은 고딕", 9, "bold"), wraplength=200, relief="solid", bd=2, padx=10, pady=10, cursor="hand2")
        lbl.pack()
        
        # 외부 웹 브라우저 연결 바인딩 (메인 로직 참조)
        from webbrowser import open as web_open
        lbl.bind("<Button-1>", lambda e: [web_open(self.current_url) if self.current_url not in ["ALARM", "TIMER", "WEATHER"] else None, self.hide()])
        
        self.update_position()
        if auto_hide: self.root.after(duration_ms, self.hide)

    def play_sequence(self, news_list, index, duration_ms):
        """여러 개의 뉴스를 순차적으로 보여줍니다."""
        if index < len(news_list):
            news = news_list[index]
            self.show(news['title'], news['url'], duration_ms, auto_hide=False)
            self.root.after(duration_ms, lambda: self.play_sequence(news_list, index + 1, duration_ms))
        else:
            self.hide()

    def hide(self):
        """말풍선을 닫습니다."""
        if self.bubble_win and self.bubble_win.winfo_exists():
            self.bubble_win.destroy()
        self.bubble_win = None

    def update_position(self):
        """로봇 위치에 맞춰 말풍선 좌표를 계산합니다."""
        if not self.bubble_win: return
        self.bubble_win.update_idletasks()
        rx, ry, rw = self.root.winfo_x(), self.root.winfo_y(), self.root.winfo_width()
        bw, bh = self.bubble_win.winfo_reqwidth(), self.bubble_win.winfo_reqheight()
        sw = self.root.winfo_screenwidth()
        
        bx = rx + (rw // 2) - (bw // 2)
        if bx + bw > sw: bx = sw - bw - 5
        if bx < 0: bx = 5
        
        # 다른 창들이 열려있을 경우 위로 쌓기 위해 최상단 Y 좌표 찾기
        highest_y = ry
        for feature in ['todo', 'folder', 'stock']:
            attr = getattr(self.bot, feature, None)
            if attr and hasattr(attr, f'{feature}_win') and getattr(attr, f'{feature}_win'):
                win = getattr(attr, f'{feature}_win')
                if win.winfo_exists(): highest_y = min(highest_y, win.winfo_y())

        self.bubble_win.geometry(f"+{bx}+{highest_y - bh - 10}")