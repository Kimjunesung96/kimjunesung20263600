import tkinter as tk
import datetime
import os
import base64
from io import BytesIO


# ---------------------------------------------------------
# 📸 스크린샷 & 클립보드 복사 기능
# ---------------------------------------------------------
class ScreenshotFeature:
    def __init__(self, root, show_bubble_func):
        self.root        = root
        self.show_bubble = show_bubble_func

        self.overlay = None
        self.canvas  = None
        self.rect    = None
        self.start_x = 0
        self.start_y = 0

    # ---------------------------------------------------------
    # DPI 배율 감지
    # ---------------------------------------------------------
    def _get_dpi_scale(self):
        try:
            import ctypes
            hwnd = self.root.winfo_id()
            dpi  = ctypes.windll.user32.GetDpiForWindow(hwnd)
            return dpi / 96.0
        except Exception:
            return 1.0

    # ---------------------------------------------------------
    # 영역 선택 오버레이 시작
    # ---------------------------------------------------------
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

        self.rect    = None
        self.start_x = 0
        self.start_y = 0

        self.canvas.bind("<ButtonPress-1>",   self.on_screen_press)
        self.canvas.bind("<B1-Motion>",        self.on_screen_drag)
        self.canvas.bind("<ButtonRelease-1>",  self.on_screen_release)
        self.overlay.bind("<Escape>", lambda e: self.overlay.destroy())

    def on_screen_press(self, event):
        self.start_x = event.x_root
        self.start_y = event.y_root
        self.rect = self.canvas.create_rectangle(
            event.x, event.y, event.x, event.y,
            outline="red", width=2, fill=""
        )

    def on_screen_drag(self, event):
        self.canvas.coords(
            self.rect,
            self.start_x - self.overlay.winfo_rootx(),
            self.start_y - self.overlay.winfo_rooty(),
            event.x, event.y
        )

    def on_screen_release(self, event):
        end_x = event.x_root
        end_y = event.y_root
        self.overlay.destroy()

        if abs(end_x - self.start_x) < 10 or abs(end_y - self.start_y) < 10:
            self.show_bubble("영역이 너무 작아 캡처가 취소되었습니다.", "ALARM", 2000, True)
            return

        self.root.after(
            200,
            lambda: self._capture_and_copy(self.start_x, self.start_y, end_x, end_y)
        )

    # ---------------------------------------------------------
    # 캡처 → 클립보드 + 파일 + 서버 저장
    # ---------------------------------------------------------
    def _capture_and_copy(self, x1, y1, x2, y2):
        try:
            import mss
            from PIL import Image
            import win32clipboard
            import requests
        except ImportError:
            self.show_bubble(
                "📸 [오류]\n터미널에서 mss, pillow를 설치해주세요!",
                "ALARM", 5000, True
            )
            return

        left   = min(x1, x2)
        top    = min(y1, y2)
        width  = abs(x2 - x1)
        height = abs(y2 - y1)
        monitor = {"top": top, "left": left, "width": width, "height": height}

        with mss.mss() as sct:
            sct_img = sct.grab(monitor)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

        # 파일 저장
        save_dir = "screenshots"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        filename = f"capture_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(save_dir, filename)
        img.save(filepath, "PNG")

        # 클립보드 저장
        output = BytesIO()
        img.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]
        output.close()

        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()

        # 서버 전송
        try:
            img_buffer = BytesIO()
            img.save(img_buffer, format="PNG")
            img_base64  = base64.b64encode(img_buffer.getvalue()).decode("utf-8")
            base64_str  = f"data:image/png;base64,{img_base64}"
            response    = requests.post(
                "http://localhost:8000/api/clipboard",
                json={"type": "image", "content": base64_str}
            )
            if response.status_code == 200:
                self.show_bubble("📸 찰칵!\n클립보드, 파일, 서버에 모두 저장됨!", "ALARM", 4000, True)
            else:
                self.show_bubble(f"📸 찰칵!\nDB 저장 실패: {response.status_code}", "ALARM", 4000, True)
        except Exception:
            self.show_bubble("📸 찰칵!\n서버가 꺼져있거나 오류가 났습니다.", "ALARM", 4000, True)