import tkinter as tk
import datetime
from tkinter import simpledialog


# ---------------------------------------------------------
# ⏳ 타이머 & 알람 기능
# ---------------------------------------------------------
class TimerAlarmFeature:
    def __init__(self, root, face_label, show_bubble_func):
        self.root       = root
        self.face_label = face_label
        self.show_bubble = show_bubble_func

        self.timer_seconds    = 0
        self.is_timer_running = False
        self.target_alarm_time = ""

    # ---------------------------------------------------------
    # ⏳ 타이머
    # ---------------------------------------------------------
    def start_timer(self, minutes):
        self.timer_seconds    = minutes * 60
        self.is_timer_running = True
        self.update_timer()

    def stop_timer(self):
        self.is_timer_running = False
        self.face_label.config(text="🤖", font=("Arial", 45))

    def update_timer(self):
        if self.timer_seconds > 0 and self.is_timer_running:
            mins, secs = divmod(self.timer_seconds, 60)
            self.face_label.config(
                text=f"⏳\n{mins:02d}:{secs:02d}",
                font=("Arial", 20, "bold")
            )
            self.timer_seconds -= 1
            self.root.after(1000, self.update_timer)

        elif self.is_timer_running and self.timer_seconds <= 0:
            self.is_timer_running = False
            self.face_label.config(text="🚨", font=("Arial", 45))
            self.show_giant_alert("⏳ 타이머 종료!", "지정하신 타이머 시간이 다 되었습니다!")

    # ---------------------------------------------------------
    # ⏰ 알람
    # ---------------------------------------------------------
    def set_alarm(self):
        time_str = simpledialog.askstring(
            "알람 설정",
            "알람 시간을 입력하세요\n(예: 08:30, 14:00)"
        )
        if time_str:
            self.target_alarm_time = time_str.strip()
            self.show_bubble(
                f"오늘 {self.target_alarm_time}에 알람이 설정되었습니다!",
                "ALARM", 3000, True
            )

    def check_alarm(self):
        if self.target_alarm_time:
            now_str = datetime.datetime.now().strftime("%H:%M")
            if now_str == self.target_alarm_time:
                self.show_bubble(
                    "⏰ 띠링! 설정하신 알람 시간입니다!\n좋은 하루 보내세요!",
                    "ALARM", 10000, False
                )
                self.target_alarm_time = ""

    # ---------------------------------------------------------
    # 🚨 전체화면 긴급 알림창
    # ---------------------------------------------------------
    def show_giant_alert(self, title, message):
        alert_win = tk.Toplevel(self.root)
        alert_win.attributes("-topmost", True)
        alert_win.overrideredirect(True)
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        alert_win.geometry(f"{sw}x{sh}+0+0")
        alert_win.configure(bg="black")
        alert_win.attributes("-alpha", 0.85)

        def click_to_reset(event):
            alert_win.destroy()
            self.face_label.config(text="🤖", font=("Arial", 45))

        alert_win.bind("<Button-1>", click_to_reset)

        frame = tk.Frame(
            alert_win, bg="#ffeb3b", bd=10,
            relief="ridge", padx=50, pady=50
        )
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            frame, text=title,
            font=("맑은 고딕", 60, "bold"),
            bg="#ffeb3b", fg="#d32f2f"
        ).pack(pady=(0, 20))

        tk.Label(
            frame, text=message,
            font=("맑은 고딕", 25, "bold"),
            bg="#ffeb3b", fg="black"
        ).pack(pady=(0, 40))

        tk.Label(
            frame, text="(🚨 한번 클릭하면 원상태로 복귀합니다)",
            font=("맑은 고딕", 12, "bold"),
            bg="#ffeb3b", fg="#5f6368"
        ).pack()