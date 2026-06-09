import threading
import asyncio
import json
import time
import os
import datetime
import sqlite3
import urllib.request
import numpy as np
import pyaudio
import queue
import tkinter as tk
from openwakeword.model import Model
from google import genai
from google.genai import types
from tkinter import simpledialog

WAKEWORD = "hey_jarvis"
NORMAL_THRESHOLD = 0.1
CONV_THRESHOLD = 0.08
CONV_DURATION = 300
SAMPLE_RATE = 16000
CHUNK = 1280
LIVE_MODEL = "gemini-3.1-flash-live-preview"

class VoiceListener:
    def __init__(self, bot, show_bubble_func):
        self.bot = bot
        self.show_bubble = show_bubble_func

        from openwakeword.utils import download_models
        print(f"\n📥 [시스템] '{WAKEWORD}' 호출어 AI 모델 확인 및 다운로드 중... (공식 서버)")
        download_models() 
        print("✅ 호출어 모델 준비 완료!\n")
        
        self.oww_model = Model(wakeword_models=["hey_jarvis"], inference_framework="onnx")
        
        self._running = False
        self._listening = False
        self.last_interaction_time = 0
        
        self.media_queue = queue.Queue()
        self.api_key = ""
        config_data = {}
        
        try:
            if os.path.exists("config.json"):
                with open("config.json", "r", encoding="utf-8") as f:
                    config_data = json.load(f)
                    self.api_key = config_data.get("gemini_api_key", "").strip()
        except Exception:
            pass

        if not self.api_key or self.api_key == "여기에_API키를_입력하세요":
            new_key = simpledialog.askstring(
                "🔑 Gemini API 키 필요",
                "등록된 Gemini API 키가 없습니다.\n발급받으신 API 키를 입력해주세요.\n(입력 시 config.json에 자동 저장됩니다.)"
            )
            if new_key and new_key.strip():
                self.api_key = new_key.strip()
                config_data["gemini_api_key"] = self.api_key
                try:
                    with open("config.json", "w", encoding="utf-8") as f:
                        json.dump(config_data, f, indent=4, ensure_ascii=False)
                    self.show_bubble("🔑 API 키가 성공적으로 저장되었습니다!", "ALARM", 3000, True)
                except Exception as e:
                    print(f"API 키 저장 실패: {e}")
            else:
                self.show_bubble("⚠️ API 키가 없어 음성 비서 기능이 작동하지 않습니다.", "ALARM", 5000, True)

    def start(self):
        if self._running: return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        print(f"🎤 자비스 음성 엔진 가동 (호출어: '{WAKEWORD}')")

    def _audio_play_worker(self, play_queue, audio_out):
        while True:
            data = play_queue.get()
            if data is None: break
            try: audio_out.write(data)
            except Exception: pass
            play_queue.task_done()

    def _loop(self):
        pa = pyaudio.PyAudio()
        try:
            stream = pa.open(rate=SAMPLE_RATE, channels=1, format=pyaudio.paInt16, input=True, frames_per_buffer=CHUNK)
        except OSError as e:
            print(f"\n❌ 마이크를 찾을 수 없거나 접근이 차단되었습니다. ({e})")
            pa.terminate()
            self._running = False
            return

        try:
            while self._running:
                raw = stream.read(CHUNK, exception_on_overflow=False)
                audio = np.frombuffer(raw, dtype=np.int16)
                if self._listening: continue
                
                prediction = self.oww_model.predict(audio)
                
                score = 0
                for k, v in prediction.items():
                    if v > score: score = v

                current_time = time.time()
                in_conv = (current_time - self.last_interaction_time) < CONV_DURATION
                active_threshold = CONV_THRESHOLD if in_conv else NORMAL_THRESHOLD
                
                if score >= active_threshold:
                    print(f"\n✅ 자비스 호출 감지! (점수: {score:.2f})")
                    self.bot.face_ctrl.set_state("listening") # 💡 [표정] 눈 번쩍! (듣는 중)
                    self.oww_model.reset()
                    self._listening = True
                    asyncio.run(self._live_api_session(stream, pa))
                    self.last_interaction_time = time.time()
                    self._listening = False
                    self.bot.face_ctrl.set_state("idle") # 💡 [표정] 대기 상태로 복귀
        finally:
            stream.stop_stream(); stream.close(); pa.terminate()

    async def _live_api_session(self, stream, pa):
        if not self.api_key: return
        client = genai.Client(api_key=self.api_key)
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        
        robot_tool = {
            "function_declarations": [
                {
                    "name": "execute_robot_command",
                    "description": "자비스 로봇의 모든 제어 기능(화면 분석, 프로그램 실행, 알람 등)을 관장합니다.",
                    "parameters": {
                        "type": "OBJECT",
                        "properties": {
                            "action": {
                                "type": "STRING",
                                "description": "명령 종류: 'timer', 'alarm', 'add_schedule', 'analyze_screen', 'open_program', 'screenshot', 'weather', 'stock', 'todo', 'folder', 'guide', 'find', 'ask_clipboard', 'add_folder', 'read_news'"
                            },
                            "folder_name": {
                                "type": "STRING",
                                "description": "새로 등록할 퀵 폴더의 별명"
                            },
                            "analyze_prompt": { "type": "STRING" },
                            "question_text": { "type": "STRING" },
                            "program_name": { "type": "STRING" },
                            "minutes": { "type": "INTEGER" },
                            "alarm_time": { "type": "STRING" },
                            "target_word": { "type": "STRING" },
                            "schedule_date": { "type": "STRING" },
                            "schedule_content": { "type": "STRING" }
                        },
                        "required": ["action"]
                    }
                }
            ]
        }

        config = types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            tools=[robot_tool],
            system_instruction=(
                f"너는 AI 비서 자비스야. 짧고 명확하게 한국어로 대답해줘. 오늘은 {today_str}이야. "
                "1. 사용자가 화면을 번역, 요약, 분석해달라고 하면 'analyze_screen' 액션을 호출해. "
                "2. 사용자가 프로그램을 열어달라고 하면 'open_program' 액션을 호출해. "
                "3. 🚨[절대 규칙] 사용자가 특정 글자나 단어를 '찾아줘'라고 하면 인터넷 검색이나 브라우저 실행을 절대 하지 마! 무조건 'find' 액션만 실행해. "
                "4. 사용자가 복사한 코드나 내용에 대해 '어떻게 해줘', '고쳐줘', '질문' 등을 말하면 'ask_clipboard' 액션을 호출해. "
                "5. 🚨[절대 규칙] 사용자가 복사한 경로를 폴더나 즐겨찾기에 등록해달라고 하면 되묻지 말고 즉시 'add_folder' 액션을 호출해. 사용자가 구체적인 폴더 이름을 말하지 않았다면 'folder_name' 파라미터는 완전히 비워두거나 절대 질문하지 마. "
                "6. 🚨[절대 규칙] 사용자가 대화를 그만하자고 하거나 '종료', '들어가봐'라고 하면, 대답에 반드시 '대화를 종료합니다'라는 문구를 포함해. "
                "7. 사용자가 '오늘 이슈', '뉴스 알려줘', '새로운 소식' 등을 물어보면 'read_news' 액션을 호출해."
                "8. 🚨[절대 규칙] 사용자가 무언가를 '추가', '등록', '넣어줘' 라고 하면 무조건 'add_schedule' 액션을 호출해. 절대 'todo'로 보내지 마. " 
                "   schedule_date는 오늘 날짜 {today_str}, schedule_content는 사용자가 말한 내용으로 채워. "
                "   'todo'는 오직 '할일 보여줘', '목록 보여줘' 처럼 조회할 때만 써. "
                "9. todo는 보여줘와 질문형일떄만 추가,등록 은 add_schedule "
                "10. 🚨[절대 규칙]'target_word'는 어느나라 언어인지 말하지 않는이상 기본적으로 한글이다"
            )
        )
        
        audio_out = pa.open(rate=24000, channels=1, format=pyaudio.paInt16, output=True)
        play_queue = queue.Queue()
        play_thread = threading.Thread(target=self._audio_play_worker, args=(play_queue, audio_out), daemon=True)
        play_thread.start()

        try:
            async with client.aio.live.connect(model=LIVE_MODEL, config=config) as session:
                print("🔊 자비스 연결됨...")
                async def send_mic():
                    try:
                        while self._listening:
                            raw = await asyncio.to_thread(stream.read, CHUNK, exception_on_overflow=False)
                            audio_arr = np.frombuffer(raw, dtype=np.int16).astype(np.float32)
                            rms = int(np.sqrt(np.mean(audio_arr ** 2)))
                            level = min(rms // 150, 20)
                            bar = "█" * level + "░" * (20 - level)
                            print(f"\r🎤 |{bar}| ", end="", flush=True)
                            await session.send_realtime_input(audio=types.Blob(data=raw, mime_type=f"audio/pcm;rate={SAMPLE_RATE}"))
                    except asyncio.CancelledError:
                        pass
                    except Exception:
                        pass
                
                send_task = asyncio.create_task(send_mic())
                should_close = False
                
                async for response in session.receive():
                    self.bot.face_ctrl.set_state("thinking") # 💡 [표정] 뱅글뱅글 (처리 중/생각 중)
                    
                    if response.tool_call:
                        for fc in response.tool_call.function_calls:
                            if fc.name == "execute_robot_command":
                                args = dict(fc.args) if fc.args else {}
                                print(f"\n⚡ [도구 호출 감지] 명령 실행: {args}")
                                handle_voice_command(args, self.bot, self.show_bubble, self)

                    if response.server_content and response.server_content.model_turn:
                        for part in response.server_content.model_turn.parts:
                            if part.text and "종료합니다" in part.text:
                                should_close = True
                            if part.inline_data: 
                                self.bot.face_ctrl.set_state("speaking") # 💡 [표정] 방긋방긋 (말하는 중)
                                play_queue.put(part.inline_data.data)
                                
                    if response.server_content and response.server_content.turn_complete:
                        while not play_queue.empty(): await asyncio.sleep(0.1)
                        await asyncio.sleep(0.6)
                        
                        if should_close:
                            break
                            
                        self.bot.face_ctrl.set_state("listening") # 💡 [표정] 답변 완료 후 다시 듣기 모드 대기
                        
                send_task.cancel()
        except Exception as e: print(f"\n❌ 세션 오류: {e}")
        finally:
            play_queue.put(None); play_thread.join(); audio_out.close()
            print("\n👌 대화 완료!")


# ---------------------------------------------------------
# 🎮 명령 실행 핸들러 (로봇 연동)
# ---------------------------------------------------------
def handle_voice_command(result, bot, show_bubble_func, voice_listener_instance=None):
    action = result.get("action", "unknown")

    if action == "analyze_screen":
        prompt = result.get("analyze_prompt", "이 화면을 한국어로 요약해줘.")
        show_bubble_func("📸 캡처 완료! 시각 지능 모델이 분석 중...", "ALARM", 3000, True)
        
        def _analyze_task():
            try:
                from PIL import ImageGrab
                client = genai.Client(api_key=voice_listener_instance.api_key)
                img = ImageGrab.grab()
                img.thumbnail((1200, 1200)) 
                
                response = client.models.generate_content(
                    model='gemini-3.1-flash-lite',
                    contents=[prompt, img]
                )
                text_content = response.text
                
                def _create_win():
                    win = tk.Toplevel(bot.root)
                    win.title("자비스 시각 분석 결과")
                    win.attributes("-topmost", True)
                    win.geometry("550x650")
                    win.configure(bg="#202124")
                    
                    lbl = tk.Label(win, text="👀 자비스 화면 분석 결과", bg="#202124", fg="#8ab4f8", font=("맑은 고딕", 14, "bold"))
                    lbl.pack(pady=10)
                    
                    frame = tk.Frame(win, bg="#202124")
                    frame.pack(expand=True, fill="both", padx=15, pady=(0, 15))
                    
                    scrollbar = tk.Scrollbar(frame)
                    scrollbar.pack(side="right", fill="y")
                    
                    txt = tk.Text(frame, bg="#303134", fg="white", font=("맑은 고딕", 11), wrap="word", yscrollcommand=scrollbar.set, padx=10, pady=10)
                    txt.pack(expand=True, fill="both")
                    scrollbar.config(command=txt.yview)
                    
                    txt.insert("1.0", text_content)
                    txt.config(state="disabled") 
                    show_bubble_func("✅ 화면 분석 완료! 창을 확인하세요.", "ALARM", 3000, True)
                    
                bot.root.after(0, _create_win)
                
            except Exception as e:
                bot.root.after(0, lambda: show_bubble_func("❌ 분석 중 오류가 발생했습니다.", "ALARM", 3000, True))
                
        if voice_listener_instance and voice_listener_instance.api_key:
            threading.Thread(target=_analyze_task, daemon=True).start()

    elif action == "open_program":
        prog = result.get("program_name", "").lower()
        cmd = None
        prog_display = prog
        
        if "vscode" in prog or "코드" in prog or "code" in prog: cmd = "code"; prog_display = "VS Code"
        elif "계산기" in prog or "calc" in prog: cmd = "calc"; prog_display = "계산기"
        elif "메모장" in prog or "notepad" in prog: cmd = "notepad"; prog_display = "메모장"
        elif "크롬" in prog or "chrome" in prog or "인터넷" in prog: cmd = "start chrome"; prog_display = "Chrome"
        elif "프롬프트" in prog or "cmd" in prog or "터미널" in prog: cmd = "start cmd"; prog_display = "명령 프롬프트"
        elif "탐색기" in prog or "폴더" in prog or "explorer" in prog: cmd = "explorer"; prog_display = "파일 탐색기"
        elif "유튜브" in prog or "youtube" in prog: cmd = "start https://www.youtube.com"; prog_display = "YouTube"
        else: cmd = f"start {prog}"
            
        if cmd:
            try:
                os.system(cmd)
                show_bubble_func(f"🚀 [{prog_display}] 실행 완료!", "ALARM", 3000, True)
            except Exception:
                show_bubble_func(f"❌ 실행 실패: {prog_display}", "ALARM", 3000, True)

    elif action == "add_schedule":
        s_date = result.get("schedule_date")
        s_content = result.get("schedule_content")
    
        # date 없으면 오늘로 fallback
        if not s_date:
            s_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
        if s_content:
            try:
                import os
                db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'news.db')
                db_path = os.path.normpath(db_path)
                conn = sqlite3.connect(db_path, timeout=30)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO schedule (date, content) VALUES (?, ?)", (s_date, s_content))
                conn.commit()
                conn.close()
                show_bubble_func(f"📅 {s_date}\n[{s_content}] 등록 완료!", "ALARM", 4000, True)
            except Exception as e:
                print(f"⚠️ 일정 DB 등록 에러: {e}")  # 이제 에러가 보임
                show_bubble_func("❌ 일정 등록 중 오류가 발생했습니다.", "ALARM", 3000, True)
        else:
            bot.toggle_todo_bubbles()

    elif action == "timer":
        minutes = int(result.get("minutes", 5))
        bot.start_timer(minutes)
        show_bubble_func(f"⏳ {minutes}분 타이머를 시작합니다.", "ALARM", 3000)

    elif action == "alarm":
        alarm_time = result.get("alarm_time")
        if alarm_time:
            bot.timer_alarm.target_alarm_time = alarm_time
            show_bubble_func(f"⏰ 오늘 {alarm_time}에 알람이 설정되었습니다!", "ALARM", 3000, True)
        else:
            bot.set_alarm()

    elif action == "ask_clipboard":
        question = result.get("question_text", "이 클립보드 내용을 분석해줘.")
        bot.process_clipboard_with_ai(question)

    elif action == "find":
        target_word = result.get("target_word")
        if target_word: bot.start_tracking_target_by_word(target_word)
        else: bot.start_guide_mode()

    elif action == "screenshot": bot.start_screenshot()
    elif action == "weather": bot._on_weather_click(None)
    elif action == "stock": bot.toggle_stock_bubbles()
    elif action == "todo": bot.toggle_todo_bubbles()
    
    elif action == "add_folder":
        try:
            import tkinter as tk
            raw_path = bot.root.clipboard_get()
            target_path = raw_path.strip().strip('"').strip("'")
            
            if not os.path.exists(target_path):
                show_bubble_func("⚠️ 클립보드 내용이 올바른 경로가 아닙니다.", "ALARM", 3000, True)
                return

            folder_name = result.get("folder_name")
            if not folder_name:
                folder_name = os.path.basename(target_path)
                if not folder_name: folder_name = "새 퀵 폴더"

            conn = sqlite3.connect('news.db', timeout=30)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO quick_folders (name, path) VALUES (?, ?)", (folder_name, target_path))
            conn.commit()
            conn.close()

            show_bubble_func(f"📁 [{folder_name}] 등록 완료!", "ALARM", 3000, True)
            if hasattr(bot, 'folder') and bot.folder.folder_win and bot.folder.folder_win.winfo_exists():
                bot.folder.draw_folder_bubbles()

        except tk.TclError: show_bubble_func("⚠️ 클립보드가 비어있습니다.", "ALARM", 3000, True)
        except Exception: show_bubble_func("❌ 폴더 등록 중 오류가 발생했습니다.", "ALARM", 3000, True)

    elif action == "read_news":
        try:
            conn = sqlite3.connect('news.db', timeout=30)
            cursor = conn.cursor()
            
            query = """
                SELECT title, ai_summary FROM news 
                WHERE title LIKE '%논란%' OR title LIKE '%단독%' OR title LIKE '%비판%' OR title LIKE '%의혹%'
                   OR ai_summary LIKE '%논란%' 
                ORDER BY created_at DESC LIMIT 1
            """
            cursor.execute(query)
            row = cursor.fetchone()

            if not row:
                cursor.execute("SELECT title, ai_summary FROM news ORDER BY created_at DESC LIMIT 1")
                row = cursor.fetchone()
                
            conn.close()

            if row: show_bubble_func(f"📰 [오늘의 핫이슈]\n{row[0]}\n\n{row[1]}", "ALARM", 8000, True)
            else: show_bubble_func("⚠️ 현재 데이터베이스에 저장된 뉴스가 없습니다.", "ALARM", 3000, True)
        except Exception:
            show_bubble_func("❌ 뉴스를 가져오는데 실패했습니다.", "ALARM", 3000, True)

    elif action == "folder": bot.toggle_folder_bubbles()
    elif action == "guide": bot.start_guide_mode()