import tkinter as tk

class ToolbarUI:
    def __init__(self, root, bot_ref):
        self.root = root
        self.bot = bot_ref
        self.toolbar_win = None
        self.btn_style = {"bg": "#3c4043", "fg": "white", "font": ("맑은 고딕", 9, "bold"), "relief": "flat", "cursor": "hand2", "padx": 8, "pady": 5}
        self.sub_btn_style = {"bg": "#1a73e8", "fg": "white", "font": ("맑은 고딕", 9, "bold"), "relief": "flat", "cursor": "hand2", "padx": 6, "pady": 4}

    def toggle(self):
        if self.toolbar_win and self.toolbar_win.winfo_exists():
            self.hide()
        else:
            self.show()

    def show(self):
        if self.toolbar_win and self.toolbar_win.winfo_exists():
            self.toolbar_win.destroy()
        
        self.toolbar_win = tk.Toplevel(self.root)
        self.toolbar_win.overrideredirect(True)
        self.toolbar_win.attributes("-topmost", True)
        self.toolbar_win.configure(bg='magenta')
        self.toolbar_win.attributes("-transparentcolor", "magenta")

        self.bar_frame = tk.Frame(self.toolbar_win, bg="#202124", padx=10, pady=5, relief="flat", bd=0)
        self.bar_frame.pack()
        self.draw_main_toolbar()

    def draw_main_toolbar(self):
        for w in self.bar_frame.winfo_children(): w.destroy()
        
        if not self.bot.timer_alarm.is_timer_running:
            tk.Button(self.bar_frame, text="⏳ 타이머", command=self.draw_timer_toolbar, **self.btn_style).pack(side="left", padx=3)
        else: 
            tk.Button(self.bar_frame, text="🛑 정지", command=lambda: [self.bot.stop_timer(), self.hide()], **self.btn_style).pack(side="left", padx=3)
        
        tk.Button(self.bar_frame, text="⏰ 알람", command=lambda: [self.bot.set_alarm(), self.hide()], **self.btn_style).pack(side="left", padx=3)
        tk.Button(self.bar_frame, text="📅 달력", command=self.bot.toggle_todo_bubbles, **self.btn_style).pack(side="left", padx=3)
        tk.Button(self.bar_frame, text="📸 캡처", command=lambda: [self.hide(), self.bot.start_screenshot()], **self.btn_style).pack(side="left", padx=3)
        tk.Button(self.bar_frame, text="💬 질문", command=self.ask_ai_clipboard, **self.btn_style).pack(side="left", padx=3)
        tk.Button(self.bar_frame, text="📁 폴더", command=self.bot.toggle_folder_bubbles, **self.btn_style).pack(side="left", padx=3)
        tk.Button(self.bar_frame, text="📈 주식", command=self.bot.toggle_stock_bubbles, **self.btn_style).pack(side="left", padx=3)
        tk.Button(self.bar_frame, text="🧭 가이드", command=lambda: [self.hide(), self.bot.start_guide_mode()], **self.btn_style).pack(side="left", padx=3)
        tk.Button(self.bar_frame, text="✖ 닫기", command=self.hide, bg="#ea4335", fg="white", font=("맑은 고딕", 9, "bold"), relief="flat", cursor="hand2", padx=8, pady=5).pack(side="left", padx=(10,3))
        self.update_position()

    def draw_timer_toolbar(self):
        for w in self.bar_frame.winfo_children(): w.destroy()
        
        def start_and_close(m):
            self.bot.start_timer(m)
            self.hide()

        def start_custom_timer(val):
            try:
                m = int(val)
                if m > 0: start_and_close(m)
            except: pass

        tk.Button(self.bar_frame, text="1분", command=lambda: start_and_close(1), **self.sub_btn_style).pack(side="left", padx=2)
        tk.Button(self.bar_frame, text="3분", command=lambda: start_and_close(3), **self.sub_btn_style).pack(side="left", padx=2)
        tk.Button(self.bar_frame, text="5분", command=lambda: start_and_close(5), **self.sub_btn_style).pack(side="left", padx=2)
        tk.Button(self.bar_frame, text="10분", command=lambda: start_and_close(10), **self.sub_btn_style).pack(side="left", padx=2)
        
        custom_var = tk.StringVar()
        entry = tk.Entry(self.bar_frame, textvariable=custom_var, width=4, font=("맑은 고딕", 10, "bold"), justify="center", bd=0)
        entry.pack(side="left", padx=(8, 2), ipady=4)
        
        tk.Button(self.bar_frame, text="확인", command=lambda: start_custom_timer(custom_var.get()), bg="#34a853", fg="white", font=("맑은 고딕", 9, "bold"), relief="flat", cursor="hand2").pack(side="left", padx=2, ipady=1)
        tk.Button(self.bar_frame, text="🔙", command=self.draw_main_toolbar, bg="#5f6368", fg="white", font=("맑은 고딕", 9), relief="flat", cursor="hand2", padx=5).pack(side="left", padx=(10, 0))
        self.update_position()

    def hide(self):
        if self.toolbar_win and self.toolbar_win.winfo_exists():
            self.toolbar_win.destroy()
        self.toolbar_win = None

    def update_position(self):
        if not self.toolbar_win or not self.toolbar_win.winfo_exists(): return
        self.toolbar_win.update_idletasks()
        sw = self.root.winfo_screenwidth()
        rx, ry, rw = self.root.winfo_x(), self.root.winfo_y(), self.root.winfo_width()
        tw, th = self.toolbar_win.winfo_reqwidth(), self.toolbar_win.winfo_reqheight()

        if rx + rw + tw + 5 <= sw: x = rx + rw + 5
        elif rx - tw - 5 >= 0: x = rx - tw - 5
        else: x = sw - tw
        y = ry + (self.root.winfo_height() // 2) - (th // 2)
        self.toolbar_win.geometry(f"+{x}+{y}")

    def ask_ai_clipboard(self):
        self.hide()
        from tkinter import simpledialog
        question = simpledialog.askstring("자비스 질문", "클립보드 내용에 대해 무엇을 할까요?\n(예: 이 코드 버그 찾아줘, 한국어로 번역해줘)")
        if question:
            self.bot.process_clipboard_with_ai(question)