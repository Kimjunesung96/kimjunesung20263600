import tkinter as tk
import sqlite3
import os
from tkinter import simpledialog
import tkinter.messagebox as messagebox


# ---------------------------------------------------------
# 📁 퀵 폴더 기능
# ---------------------------------------------------------
class FolderFeature:
    def __init__(self, root, show_bubble_func):
        self.root        = root
        self.show_bubble = show_bubble_func
        self.folder_win  = None

    # ---------------------------------------------------------
    # DB 조회
    # ---------------------------------------------------------
    def get_quick_folders(self):
        try:
            conn = sqlite3.connect('news.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS quick_folders (
                                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT,
                                path TEXT)''')
            cursor.execute("SELECT id, name, path FROM quick_folders ORDER BY id ASC")
            rows = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return rows
        except Exception:
            return []

    # ---------------------------------------------------------
    # 토글
    # ---------------------------------------------------------
    def toggle_folder_bubbles(self):
        if self.folder_win and self.folder_win.winfo_exists():
            self.folder_win.destroy()
            self.folder_win = None
        else:
            self.draw_folder_bubbles()

    # ---------------------------------------------------------
    # 버블 그리기
    # ---------------------------------------------------------
    def draw_folder_bubbles(self):
        if self.folder_win and self.folder_win.winfo_exists():
            self.folder_win.destroy()

        self.folder_win = tk.Toplevel(self.root)
        self.folder_win.overrideredirect(True)
        self.folder_win.attributes("-topmost", True)
        self.folder_win.configure(bg='#202124')

        container = tk.Frame(
            self.folder_win, bg='#202124',
            padx=15, pady=15, relief="ridge", bd=2
        )
        container.pack()

        tk.Label(
            container, text="📁 퀵 폴더",
            bg='#202124', fg="white",
            font=("맑은 고딕", 10, "bold")
        ).pack(side="top", pady=(0, 10))

        items = self.get_quick_folders()

        def open_folder(path):
            try:
                os.startfile(path)
            except Exception:
                self.show_bubble(
                    "❌ 경로를 열 수 없습니다.\n경로가 올바른지 확인해주세요.",
                    "ALARM", 3000, True
                )

        def delete_folder(e, folder_id):
            if messagebox.askyesno("삭제", "이 폴더를 즐겨찾기에서 지우시겠습니까?"):
                conn = sqlite3.connect('news.db')
                cursor = conn.cursor()
                cursor.execute("DELETE FROM quick_folders WHERE id=?", (folder_id,))
                conn.commit()
                conn.close()
                self.draw_folder_bubbles()

        def add_new_folder():
            name = simpledialog.askstring(
                "퀵 폴더 등록",
                "폴더의 별명을 입력하세요\n(예: 인공지능 과제)"
            )
            if not name:
                return
            path = simpledialog.askstring(
                "퀵 폴더 등록",
                "복사한 폴더 경로를 붙여넣으세요\n(예: C:\\Users\\... )"
            )
            if not path:
                return
            try:
                conn = sqlite3.connect('news.db')
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO quick_folders (name, path) VALUES (?, ?)",
                    (name, path)
                )
                conn.commit()
                conn.close()
                self.draw_folder_bubbles()
            except Exception:
                pass

        add_btn = tk.Label(
            container, text="➕ 새 폴더 등록",
            bg="#fbbc05", fg="black",
            font=("맑은 고딕", 9, "bold"),
            relief="flat", padx=15, pady=6, cursor="hand2"
        )
        add_btn.pack(side="bottom", pady=(10, 0), fill="x")
        add_btn.bind("<Button-1>", lambda e: add_new_folder())

        for item in reversed(items):
            frame = tk.Frame(container, bg='#202124')
            frame.pack(side="bottom", pady=2, fill="x")

            lbl = tk.Label(
                frame, text=f" {item['name']}",
                bg="#3c4043", fg="white",
                font=("맑은 고딕", 10),
                relief="flat", padx=12, pady=6,
                cursor="hand2", anchor="w"
            )
            lbl.pack(side="left", fill="x", expand=True)
            lbl.bind("<Button-1>", lambda e, p=item['path']: open_folder(p))

            del_btn = tk.Label(
                frame, text="✖",
                bg="#ea4335", fg="white",
                font=("Arial", 8, "bold"),
                relief="flat", padx=8, pady=6, cursor="hand2"
            )
            del_btn.pack(side="right", padx=(2, 0))
            del_btn.bind("<Button-1>", lambda e, i=item['id']: delete_folder(e, i))

        self.folder_win.update_idletasks()
        self.update_folder_position()

    # ---------------------------------------------------------
    # 위치 갱신 (로봇 위에 붙이기)
    # ---------------------------------------------------------
    def update_folder_position(self):
        if self.folder_win and self.folder_win.winfo_exists():
            rx = self.root.winfo_x()
            ry = self.root.winfo_y()
            rw = self.root.winfo_width()
            tw = self.folder_win.winfo_reqwidth()
            th = self.folder_win.winfo_reqheight()
            tx = rx + (rw // 2) - (tw // 2)
            ty = ry - th - 5
            self.folder_win.geometry(f"+{tx}+{ty}")