import tkinter as tk
import time
import base64
from PIL import ImageGrab


# ---------------------------------------------------------
# 🧭 가이드 모드 HUD
# ---------------------------------------------------------
class GuideFeature:
    def __init__(self, root, show_bubble_func, ocr_feature):
        self.root        = root
        self.show_bubble = show_bubble_func
        self.ocr         = ocr_feature   # GuideOcrFeature 참조

        self.current_guide_step = 0

    # ---------------------------------------------------------
    # 대본 입력 다이얼로그
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

        tk.Label(
            dialog,
            text="📝 대본을 입력하세요. (엔터 3번으로 단계 구분)",
            font=("맑은 고딕", 12, "bold"),
            bg="#202124", fg="white"
        ).pack(pady=10)

        input_area = tk.Text(
            dialog, font=("맑은 고딕", 11), wrap="word",
            bg="#3c4043", fg="white", insertbackground="white"
        )
        input_area.pack(fill="both", expand=True, padx=15, pady=5)

        guide_text = ""

        def on_submit():
            nonlocal guide_text
            guide_text = input_area.get("1.0", "end-1c")
            dialog.destroy()

        tk.Button(
            dialog, text="✅ 확인 (대본 입력 완료)",
            command=on_submit,
            bg="#4CAF50", fg="white",
            font=("맑은 고딕", 12, "bold"), padx=20
        ).pack(pady=10)

        dialog.grab_set()
        self.root.wait_window(dialog)

        if not guide_text.strip():
            return

        steps = [s.strip() for s in guide_text.split('\n\n\n') if s.strip()]
        if not steps:
            return

        self.current_guide_step = 0
        self._build_guide_hud(steps)

    # ---------------------------------------------------------
    # HUD 창 구성
    # ---------------------------------------------------------
    def _build_guide_hud(self, steps):
        hud = tk.Toplevel(self.root)
        hud.overrideredirect(True)
        hud.attributes("-topmost", True)
        hud.configure(bg="#2b2b2b")

        def follow_robot():
            if hud.winfo_exists():
                rx = self.root.winfo_x()
                ry = self.root.winfo_y()
                rw = self.root.winfo_width()
                hw = hud.winfo_reqwidth()
                hh = hud.winfo_reqheight()
                tx = rx - hw - 15
                ty = ry + (rw // 2) - (hh // 2)
                hud.geometry(f"+{tx}+{ty}")
                hud.after(20, follow_robot)

        follow_robot()

        step_header = tk.Label(
            hud, text="",
            font=("맑은 고딕", 10, "bold"),
            fg="#fbbc05", bg="#2b2b2b"
        )
        step_header.pack(pady=(8, 4))

        word_frame     = tk.Frame(hud, bg="#2b2b2b")
        word_frame.pack(padx=10, pady=(0, 6), fill="x")

        selected_btns  = []
        selected_words = []

        def clear_word_buttons():
            for w in word_frame.winfo_children():
                w.destroy()

        def clear_selection():
            for b in selected_btns:
                if b.winfo_exists():
                    b.config(bg="#3c4043", fg="white")
            selected_btns.clear()
            selected_words.clear()
            selected_label.config(text="선택: 없음")

        def search_selected():
            if not selected_words:
                return
            self.ocr.start_tracking_target_by_word(" ".join(selected_words))

        search_bar = tk.Frame(hud, bg="#2b2b2b")
        search_bar.pack(fill="x", padx=10, pady=(0, 4))

        selected_label = tk.Label(
            search_bar, text="선택: 없음",
            font=("맑은 고딕", 8), fg="#aaaaaa", bg="#2b2b2b"
        )
        selected_label.pack(side="left", expand=True, anchor="w")

        tk.Button(
            search_bar, text="🔍 검색",
            font=("맑은 고딕", 9, "bold"),
            bg="#1a73e8", fg="white",
            relief="flat", cursor="hand2", padx=8, pady=2,
            command=search_selected
        ).pack(side="right", padx=(4, 0))

        tk.Button(
            search_bar, text="✖ 초기화",
            font=("맑은 고딕", 9),
            bg="#5f6368", fg="white",
            relief="flat", cursor="hand2", padx=6, pady=2,
            command=lambda: clear_selection()
        ).pack(side="right", padx=2)

        def build_word_buttons(text):
            clear_word_buttons()
            selected_btns.clear()
            selected_words.clear()
            selected_label.config(text="선택: 없음")

            row_frame = None
            for i, word in enumerate(text.split()):
                if i % 6 == 0:
                    row_frame = tk.Frame(word_frame, bg="#2b2b2b")
                    row_frame.pack(anchor="w", pady=1)

                btn = tk.Button(
                    row_frame, text=word,
                    font=("맑은 고딕", 9, "bold"),
                    bg="#3c4043", fg="white",
                    relief="flat", cursor="hand2", padx=6, pady=3
                )
                btn.pack(side="left", padx=2)

                def on_click(b=btn, w=word):
                    if b in selected_btns:
                        b.config(bg="#3c4043", fg="white")
                        selected_btns.remove(b)
                        selected_words.remove(w)
                    else:
                        b.config(bg="#e91e63", fg="white")
                        selected_btns.append(b)
                        selected_words.append(w)
                    selected_label.config(
                        text=f"선택: {' '.join(selected_words)}" if selected_words else "선택: 없음"
                    )

                btn.config(command=on_click)

        def update_hud():
            if self.current_guide_step >= len(steps):
                clear_word_buttons()
                step_header.config(text="✅ 가이드 완료!")
                btn_next.config(state="disabled")
                hud.after(3000, hud.destroy)
                return
            idx = self.current_guide_step
            step_header.config(text=f"[{idx + 1} / {len(steps)}]")
            build_word_buttons(steps[idx])

        def next_step():
            self.current_guide_step += 1
            self.ocr.kill_all_tracking()
            update_hud()

        def on_close():
            self.ocr.kill_all_tracking()
            hud.destroy()

        def report_error():
            hud.withdraw()
            self.root.update()
            time.sleep(0.3)
            try:
                from io import BytesIO
                import requests as _req
                import tkinter.messagebox as messagebox

                img       = ImageGrab.grab()
                buf       = BytesIO()
                img.save(buf, format="PNG")
                img_b64   = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
                error_msg = f"🚨 [오류 발생 단계] {steps[self.current_guide_step]}"

                _req.post("http://localhost:8000/api/clipboard", json={"type": "text",  "content": error_msg})
                _req.post("http://localhost:8000/api/clipboard", json={"type": "image", "content": img_b64})
                messagebox.showinfo("오류 캡처 완료", "리액트 클립보드에 자동 저장되었습니다!")
            except Exception:
                pass
            hud.deiconify()

        btn_frame = tk.Frame(hud, bg="#2b2b2b")
        btn_frame.pack(side="bottom", pady=10)

        btn_next = tk.Button(
            btn_frame, text="▶ 다음", command=next_step,
            bg="#4CAF50", fg="white", font=("맑은 고딕", 10, "bold")
        )
        btn_next.pack(side="left", padx=5)

        tk.Button(
            btn_frame, text="🚨 오류", command=report_error,
            bg="#f44336", fg="white", font=("맑은 고딕", 10, "bold")
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame, text="✖ 종료", command=on_close,
            bg="#5f6368", fg="white", font=("맑은 고딕", 10, "bold")
        ).pack(side="left", padx=5)

        update_hud()