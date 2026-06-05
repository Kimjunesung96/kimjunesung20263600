import tkinter as tk
import sys
import queue

class TerminalHUD:
    def __init__(self, root):
        self.root = root
        self.win = tk.Toplevel(root)
        self.win.title("J.A.R.V.I.S. Terminal")
        self.win.attributes("-topmost", True)
        self.win.attributes("-alpha", 0.85)
        self.win.configure(bg="#1e1e1e")
        self.win.overrideredirect(True)

        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        w, h = 450, 200
        self.win.geometry(f"{w}x{h}+{sw - w - 20}+{sh - h - 60}")

        self.header = tk.Frame(self.win, bg="#333333", height=22)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)
        
        lbl = tk.Label(self.header, text="💻 J.A.R.V.I.S. System Log", bg="#333333", fg="#00FF00", font=("Consolas", 9, "bold"))
        lbl.pack(side="left", padx=5)

        self.header.bind("<Button-1>", self.start_move)
        self.header.bind("<B1-Motion>", self.do_move)
        lbl.bind("<Button-1>", self.start_move)
        lbl.bind("<B1-Motion>", self.do_move)

        self.text_widget = tk.Text(self.win, bg="#1e1e1e", fg="#00FF00", font=("Consolas", 10),
                                   wrap="word", relief="flat", highlightthickness=0)
        self.text_widget.pack(expand=True, fill="both", padx=5, pady=5)
        self.text_widget.config(state="disabled")

        self.queue = queue.Queue()
        self.hide_timer_id = None # 숨김 예약 취소용 타이머 ID
        
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        sys.stdout = self
        sys.stderr = self

        self.process_queue()
        
        # 💡 [핵심 1] 처음 봇을 켤 때는 터미널 창을 안 보이게 숨겨둡니다.
        self.win.withdraw()

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.win.winfo_x() + deltax
        y = self.win.winfo_y() + deltay
        self.win.geometry(f"+{x}+{y}")

    # 💡 [핵심 2] 화면에 나타나는 함수
    def show(self):
        # 만약 숨김 예약이 걸려있다면 취소하고 계속 띄워둠
        if self.hide_timer_id:
            self.root.after_cancel(self.hide_timer_id)
            self.hide_timer_id = None
            
        self.win.deiconify()
        self.text_widget.see("end")

    # 💡 [핵심 3] 화면에서 사라지는 함수
    def hide(self):
        self.win.withdraw()

    # 💡 [핵심 4] 찍히는 글자를 실시간으로 감시하는 마법의 로직
    def write(self, string):
        self.original_stdout.write(string) 
        self.queue.put(string)

        if "자비스 호출 감지" in string:
            self.root.after(0, self.show) # 즉시 팝업!
        elif "대화 완료" in string or "세션 오류" in string:
            # 대화가 끝나면 결과를 볼 수 있게 2초(2000ms) 뒤에 스르륵 숨김!
            self.hide_timer_id = self.root.after(2000, self.hide)

    def flush(self):
        self.original_stdout.flush()

    def process_queue(self):
        try:
            while True:
                text = self.queue.get_nowait()
                self.text_widget.config(state="normal")
                
                if text.startswith("\r"):
                    self.text_widget.delete("end-1c linestart", "end-1c")
                    text = text.replace("\r", "")
                    
                self.text_widget.insert("end", text)
                self.text_widget.see("end") 
                self.text_widget.config(state="disabled")
        except queue.Empty:
            pass
        
        self.root.after(50, self.process_queue)