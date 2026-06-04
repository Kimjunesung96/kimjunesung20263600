import tkinter as tk
import sqlite3
import threading
import urllib.parse
import webbrowser


# ---------------------------------------------------------
# 💡 주식 자동 갱신 주기 (초)
# ---------------------------------------------------------
STOCK_REFRESH_SECONDS = 30


# ---------------------------------------------------------
# 📈 주식 전광판 기능
# ---------------------------------------------------------
class StockFeature:
    def __init__(self, root, show_bubble_func):
        self.root        = root
        self.show_bubble = show_bubble_func
        self.stock_win   = None
        self._stock_refresh_id = None

    # ---------------------------------------------------------
    # DB 조회
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

    # ---------------------------------------------------------
    # 토글
    # ---------------------------------------------------------
    def toggle_stock_bubbles(self):
        if self.stock_win and self.stock_win.winfo_exists():
            if self._stock_refresh_id:
                self.root.after_cancel(self._stock_refresh_id)
                self._stock_refresh_id = None
            self.stock_win.destroy()
            self.stock_win = None
        else:
            self.draw_stock_bubbles()

    # ---------------------------------------------------------
    # 버블 그리기
    # ---------------------------------------------------------
    def draw_stock_bubbles(self):
        if self.stock_win and self.stock_win.winfo_exists():
            self.stock_win.destroy()

        self.stock_win = tk.Toplevel(self.root)
        self.stock_win.overrideredirect(True)
        self.stock_win.attributes("-topmost", True)
        self.stock_win.configure(bg='#202124')

        container = tk.Frame(
            self.stock_win, bg='#202124',
            padx=15, pady=15, relief="ridge", bd=2
        )
        container.pack()

        tk.Label(
            container, text="📈 관심 주식",
            bg='#202124', fg="white",
            font=("맑은 고딕", 10, "bold")
        ).pack(side="top", pady=(0, 10))

        loading_lbl = tk.Label(
            container, text="📡 불러오는 중...",
            bg="#3c4043", fg="white",
            font=("맑은 고딕", 9),
            relief="flat", padx=10, pady=5
        )
        loading_lbl.pack(side="bottom", pady=2, fill="x")

        self.stock_win.update_idletasks()
        self.update_stock_position()

        def fetch_stocks():
            import requests
            stocks  = self.get_favorite_stocks_from_db()

            if not stocks:
                self.root.after(0, render_empty)
                return

            results = []
            for stock in stocks:
                try:
                    res = requests.get(
                        f"http://localhost:8000/api/stock/{stock['ticker']}",
                        timeout=10
                    ).json()
                    results.append({"name": stock["name"], "data": res})
                except Exception:
                    results.append({"name": stock["name"], "data": {"status": "error"}})

            self.root.after(0, lambda: render_stocks(results))

        def render_empty():
            if not self.stock_win or not self.stock_win.winfo_exists():
                return
            loading_lbl.destroy()
            tk.Label(
                container, text="등록된 종목이 없습니다",
                bg="#3c4043", fg="#b0b0b0",
                font=("맑은 고딕", 10),
                relief="flat", padx=12, pady=6
            ).pack(side="bottom", pady=2, fill="x")
            self.stock_win.update_idletasks()
            self.update_stock_position()

        def render_stocks(results):
            if not self.stock_win or not self.stock_win.winfo_exists():
                return
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
                        bg_color, fg_color, arrow = "#f1f3f4", "black",    "➖"

                    text = f"{name} : {price:,.2f} ({arrow} {abs(pct)}%)"
                else:
                    bg_color, fg_color = "#3c4043", "#b0b0b0"
                    text = f"{name} : 정보 없음"

                lbl = tk.Label(
                    container, text=text,
                    bg=bg_color, fg=fg_color,
                    font=("맑은 고딕", 10, "bold"),
                    relief="flat", padx=12, pady=6,
                    anchor="w", cursor="hand2"
                )
                lbl.pack(side="bottom", pady=2, fill="x")
                lbl.bind("<Button-1>", lambda e, n=name: self.on_stock_click(n))

            self.stock_win.update_idletasks()
            self.update_stock_position()

            if self.stock_win and self.stock_win.winfo_exists():
                self._stock_refresh_id = self.root.after(
                    STOCK_REFRESH_SECONDS * 1000,
                    self.draw_stock_bubbles
                )

        threading.Thread(target=fetch_stocks, daemon=True).start()

    # ---------------------------------------------------------
    # 위치 갱신 (로봇 위에 붙이기)
    # ---------------------------------------------------------
    def update_stock_position(self):
        if self.stock_win and self.stock_win.winfo_exists():
            rx = self.root.winfo_x()
            ry = self.root.winfo_y()
            rw = self.root.winfo_width()
            tw = self.stock_win.winfo_reqwidth()
            th = self.stock_win.winfo_reqheight()
            tx = rx + (rw // 2) - (tw // 2)
            ty = ry - th - 5
            self.stock_win.geometry(f"+{tx}+{ty}")

    # ---------------------------------------------------------
    # 종목 클릭 → 리액트 웹으로 검색
    # ---------------------------------------------------------
    def on_stock_click(self, stock_name):
        safe_name  = urllib.parse.quote(stock_name)
        target_url = f"http://localhost:5173/?search={safe_name}"
        webbrowser.open(target_url)