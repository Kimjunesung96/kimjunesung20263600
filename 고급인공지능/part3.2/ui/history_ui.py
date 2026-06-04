import tkinter as tk
from core.settings import get_settings, save_custom_keyword

class HistoryUI:
    def __init__(self, root, get_news_from_db_callback, open_and_close_callback):
        self.root = root
        self.get_news_from_db = get_news_from_db_callback
        self.open_and_close = open_and_close_callback
        self.history_win = None

    def toggle(self):
        if self.history_win and self.history_win.winfo_exists():
            self.hide()
        else:
            self.show()

    def show(self):
        if self.history_win and self.history_win.winfo_exists():
            self.history_win.destroy()
        
        settings = get_settings()
        self.history_win = tk.Toplevel(self.root)
        self.history_win.overrideredirect(True)
        self.history_win.attributes("-topmost", True)
        self.history_win.configure(bg='magenta')
        self.history_win.attributes("-transparentcolor", "magenta")

        main_frame = tk.Frame(self.history_win, bg="white", relief="solid", bd=2)
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
        lbl_dash = tk.Label(btn_frame, text="🌐 리액트 대시보드 열기", bg="#e3f2fd", fg="#1a73e8", font=("맑은 고딕", 9, "bold"), cursor="hand2", padx=5, pady=8)
        lbl_dash.pack(fill="x", pady=(5, 0))
        lbl_dash.bind("<Button-1>", lambda e: self.open_and_close("http://localhost:8000", "history"))

        middle_frame = tk.Frame(main_frame, bg="white")
        middle_frame.pack(fill="both", expand=True, side="top")

        canvas = tk.Canvas(middle_frame, bg="white", highlightthickness=0, width=290, height=350)
        scrollbar = tk.Scrollbar(middle_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(frame_id, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.history_win.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def load_news_list(keyword=""):
            for widget in scrollable_frame.winfo_children(): widget.destroy()
            items = self.get_news_from_db(settings["news_count"], keyword)
            if not items:
                tk.Label(scrollable_frame, text=f"'{keyword}' 관련 뉴스가 없습니다." if keyword else "아직 뉴스가 없습니다.", bg="white", font=("맑은 고딕", 9)).pack(pady=20)
            else:
                for item in items:
                    lbl = tk.Label(scrollable_frame, text=f"💬 {item['title']}", bg="white", fg="#202124", font=("맑은 고딕", 9), anchor="w", relief="solid", bd=1, padx=5, pady=8, cursor="hand2")
                    lbl.pack(pady=2, padx=5, fill="x")
                    lbl.bind("<Enter>", lambda e, l=lbl: l.config(bg="#e8f0fe", fg="#1a73e8"))
                    lbl.bind("<Leave>", lambda e, l=lbl: l.config(bg="white", fg="#202124"))
                    lbl.bind("<Button-1>", lambda e, u=item['url']: self.open_and_close(u, "history"))
            canvas.yview_moveto(0)

        load_news_list(settings["custom_keyword"])

        def start_resize(e):
            self.history_win._resize_start_x = e.x_root
            self.history_win._resize_start_y = e.y_root
            self.history_win._init_width = self.history_win.winfo_width()
            self.history_win._init_height = self.history_win.winfo_height()
            self.history_win._x = self.history_win.winfo_x()
            self.history_win._y = self.history_win.winfo_y()

        def do_resize(e):
            new_w = max(250, self.history_win._init_width + (e.x_root - self.history_win._resize_start_x))
            new_h = max(200, self.history_win._init_height + (e.y_root - self.history_win._resize_start_y))
            self.history_win.geometry(f"{new_w}x{new_h}+{self.history_win._x}+{self.history_win._y}")

        resizer.bind("<ButtonPress-1>", start_resize)
        resizer.bind("<B1-Motion>", do_resize)
        self.update_position()

    def hide(self):
        if self.history_win and self.history_win.winfo_exists():
            self.history_win.destroy()
        self.history_win = None

    def update_position(self):
        if not self.history_win or not self.history_win.winfo_exists(): return
        self.history_win.update_idletasks()
        rx, ry, rw = self.root.winfo_x(), self.root.winfo_y(), self.root.winfo_width()
        hw, hh = self.history_win.winfo_reqwidth(), self.history_win.winfo_reqheight()
        sw = self.root.winfo_screenwidth()
        
        if rx + rw + hw + 5 <= sw: hx = rx + rw + 5
        elif rx - hw - 5 >= 0: hx = rx - hw - 5
        else: hx = sw - hw
        self.history_win.geometry(f"+{hx}+{ry - hh - 10}")