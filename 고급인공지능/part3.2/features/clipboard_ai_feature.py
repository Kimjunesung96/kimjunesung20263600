import tkinter as tk
import threading
import json
import os
from google import genai

class ClipboardAiFeature:
    def __init__(self, root, show_bubble_func):
        self.root = root
        self.show_bubble = show_bubble_func

    def process_clipboard_with_ai(self, custom_prompt):
        try:
            copied_text = self.root.clipboard_get()
        except tk.TclError:
            self.show_bubble("⚠️ 클립보드에 텍스트가 없습니다.", "ALARM", 3000, True)
            return

        self.show_bubble("🧠 AI가 클립보드를 분석 중입니다...", "ALARM", 3000, True)

        def _task():
            try:
                # config.json에서 API 키 직접 읽어오기
                api_key = ""
                if os.path.exists("config.json"):
                    with open("config.json", "r", encoding="utf-8") as f:
                        api_key = json.load(f).get("gemini_api_key", "")
                
                if not api_key:
                    self.root.after(0, lambda: self.show_bubble("⚠️ API 키가 없습니다.", "ALARM", 3000, True))
                    return

                client = genai.Client(api_key=api_key)
                
                # 클립보드 내용과 질문을 결합하여 전송
                prompt = f"{custom_prompt}\n\n[클립보드 내용]\n{copied_text}"
                
                response = client.models.generate_content(
                    model='gemini-3.1-flash-lite', 
                    contents=prompt
                )
                
                result_text = response.text.strip()
                
                # 1. 클립보드 장전 (미리 컨트롤V 장전)
                self.root.clipboard_clear()
                self.root.clipboard_append(result_text)
                self.root.update()

                # 2. 결과물 창 열어서 전달
                def _create_win():
                    win = tk.Toplevel(self.root)
                    win.title("자비스 AI 답변")
                    win.attributes("-topmost", True)
                    win.geometry("600x700")
                    win.configure(bg="#202124")
                    
                    lbl = tk.Label(win, text="✨ 자비스 처리 결과 (클립보드 복사 완료)", bg="#202124", fg="#34a853", font=("맑은 고딕", 14, "bold"))
                    lbl.pack(pady=10)
                    
                    frame = tk.Frame(win, bg="#202124")
                    frame.pack(expand=True, fill="both", padx=15, pady=(0, 15))
                    
                    scrollbar = tk.Scrollbar(frame)
                    scrollbar.pack(side="right", fill="y")
                    
                    txt = tk.Text(frame, bg="#303134", fg="white", font=("맑은 고딕", 11), wrap="word", yscrollcommand=scrollbar.set, padx=10, pady=10)
                    txt.pack(expand=True, fill="both")
                    scrollbar.config(command=txt.yview)
                    
                    txt.insert("1.0", result_text)
                    txt.config(state="disabled") 
                    
                    self.show_bubble("✅ 처리 완료! (Ctrl+V로 바로 붙여넣으세요)", "ALARM", 4000, True)
                    
                self.root.after(0, _create_win)
            except Exception as e:
                self.root.after(0, lambda err=e: self.show_bubble(f"❌ AI 처리 오류: {err}", "ALARM", 3000, True))

        threading.Thread(target=_task, daemon=True).start()