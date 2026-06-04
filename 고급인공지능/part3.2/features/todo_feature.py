import tkinter as tk
import sqlite3
import datetime


# ---------------------------------------------------------
# 📅 할 일 타워 기능
# ---------------------------------------------------------
class TodoFeature:
    def __init__(self, root, show_bubble_func):
        self.root        = root
        self.show_bubble = show_bubble_func
        self.todo_win    = None

    # ---------------------------------------------------------
    # DB 조회
    # ---------------------------------------------------------
    def get_today_schedules(self):
        try:
            conn = sqlite3.connect('news.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            today_str = datetime.datetime.now().strftime("%Y-%m-%d")
            cursor.execute(
                "SELECT id, content FROM schedule WHERE date = ? ORDER BY id ASC",
                (today_str,)
            )
            rows = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return rows
        except Exception:
            return []

    # ---------------------------------------------------------
    # 토글
    # ---------------------------------------------------------
    def toggle_todo_bubbles(self):
        if self.todo_win and self.todo_win.winfo_exists():
            self.todo_win.destroy()
            self.todo_win = None
        else:
            self.draw_todo_bubbles()

    # ---------------------------------------------------------
    # 버블 그리기
    # ---------------------------------------------------------
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

        container = tk.Frame(
            self.todo_win, bg='#202124',
            padx=15, pady=15, relief="ridge", bd=2
        )
        container.pack()

        tk.Label(
            container, text="📅 오늘 할 일",
            bg='#202124', fg="white",
            font=("맑은 고딕", 10, "bold")
        ).pack(side="top", pady=(0, 10))

        def mark_done(event, lbl):
            if lbl.cget("bg") != "#1a73e8":
                lbl.config(bg="#1a73e8", fg="white",
                           text=lbl.cget("text") + " (✔완료)")

        for item in reversed(items):
            lbl = tk.Label(
                container,
                text=f"📌 {item['content']}",
                bg="#3c4043", fg="white",
                font=("맑은 고딕", 10),
                relief="flat", padx=12, pady=6,
                cursor="hand2", anchor="w"
            )
            lbl.pack(side="bottom", pady=2, fill="x")
            lbl.bind("<Button-1>", lambda e, l=lbl: mark_done(e, l))

        self.todo_win.update_idletasks()
        self.update_todo_position()

    # ---------------------------------------------------------
    # 위치 갱신 (로봇 위에 붙이기)
    # ---------------------------------------------------------
    def update_todo_position(self):
        if self.todo_win and self.todo_win.winfo_exists():
            rx  = self.root.winfo_x()
            ry  = self.root.winfo_y()
            rw  = self.root.winfo_width()
            tw  = self.todo_win.winfo_reqwidth()
            th  = self.todo_win.winfo_reqheight()
            tx  = rx + (rw // 2) - (tw // 2)
            ty  = ry - th - 5
            self.todo_win.geometry(f"+{tx}+{ty}")