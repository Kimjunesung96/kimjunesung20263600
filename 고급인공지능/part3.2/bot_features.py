import tkinter as tk
import threading
from features.face_feature import FaceFeature
from features.weather_feature import WeatherFeature
from features.timer_alarm_feature import TimerAlarmFeature
from features.todo_feature import TodoFeature
from features.screenshot_feature import ScreenshotFeature
from features.folder_feature import FolderFeature
from features.stock_feature import StockFeature
from features.ocr_feature import OcrFeature
from features.guide_feature import GuideFeature
from features.clipboard_ai_feature import ClipboardAiFeature

# ---------------------------------------------------------
# 🤖 AssistantFeatures — 모든 기능 조립
# ---------------------------------------------------------
class AssistantFeatures:
    def __init__(self, root, face_label, show_bubble_func):
        self.root        = root
        self.face_label  = face_label
        self.show_bubble = show_bubble_func

        # ── 기능 모듈 초기화 ──────────────────────────────
        self.timer_alarm = TimerAlarmFeature(root, face_label, show_bubble_func)
        self.todo        = TodoFeature(root, show_bubble_func)
        self.screenshot  = ScreenshotFeature(root, show_bubble_func)
        self.folder      = FolderFeature(root, show_bubble_func)
        self.stock       = StockFeature(root, show_bubble_func)
        self.ocr         = OcrFeature(root, show_bubble_func)
        self.guide       = GuideFeature(root, show_bubble_func, self.ocr)
        self.clipboard_ai = ClipboardAiFeature(root, show_bubble_func)
        
        # 💡 [추가] 얼굴 표정 컨트롤러 장착
        self.face_ctrl    = FaceFeature(root, face_label)
        # ── 날씨 위젯 (루트 창에 직접 붙는 UI) ───────────
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

        self.weather_label.bind("<Button-1>", self._on_weather_click)
        self.current_weather_briefing = "날씨 정보를 불러오는 중입니다..."
        self._update_weather()

    # ── 날씨 ─────────────────────────────────────────────
    def _on_weather_click(self, event):
        self.show_bubble(self.current_weather_briefing, "WEATHER", 20000, True)

    def _update_weather(self):
        def fetch():
            icon, briefing = WeatherFeature.get_weather_briefing("서울")
            self.current_weather_briefing = briefing
            self.root.after(0, lambda: self.weather_label.config(text=icon))
            self.root.after(1800000, self._update_weather)
        threading.Thread(target=fetch, daemon=True).start()

    # ── 타이머 & 알람 (위임) ─────────────────────────────
    def start_timer(self, minutes):
        self.timer_alarm.start_timer(minutes)

    def stop_timer(self):
        self.timer_alarm.stop_timer()

    def set_alarm(self):
        self.timer_alarm.set_alarm()

    def check_alarm(self):
        self.timer_alarm.check_alarm()

    def show_giant_alert(self, title, message):
        self.timer_alarm.show_giant_alert(title, message)

    # ── 할 일 (위임) ─────────────────────────────────────
    def toggle_todo_bubbles(self):
        self.todo.toggle_todo_bubbles()

    def update_todo_position(self):
        self.todo.update_todo_position()

    # ── 스크린샷 (위임) ──────────────────────────────────
    def start_screenshot(self):
        self.screenshot.start_screenshot()

    # ── 퀵 폴더 (위임) ───────────────────────────────────
    def toggle_folder_bubbles(self):
        self.folder.toggle_folder_bubbles()

    def update_folder_position(self):
        self.folder.update_folder_position()

    # ── 주식 (위임) ──────────────────────────────────────
    def toggle_stock_bubbles(self):
        self.stock.toggle_stock_bubbles()

    def update_stock_position(self):
        self.stock.update_stock_position()

    # ── 가이드 & OCR (위임) ──────────────────────────────
    def start_guide_mode(self):
        self.guide.start_guide_mode()
# ── [추가됨] 클립보드 AI (위임) ─────────────────────────────
    def process_clipboard_with_ai(self, custom_prompt):
        self.clipboard_ai.process_clipboard_with_ai(custom_prompt)

    def kill_all_tracking(self):
        self.ocr.kill_all_tracking()

    def start_tracking_target(self, text_widget):
        self.ocr.start_tracking_target(text_widget)

    def start_tracking_target_by_word(self, target_text):
        self.ocr.start_tracking_target_by_word(target_text)

    # ── [추가됨] AI 표정 변화 컨트롤러 ─────────────────────────────
    def set_face(self, face_text, size=45):
        # 텍스트(표정)와 폰트 크기를 실시간으로 변경합니다.
        self.root.after(0, lambda: self.face_label.config(text=face_text, font=("Arial", size)))