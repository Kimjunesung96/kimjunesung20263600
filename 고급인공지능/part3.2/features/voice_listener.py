import threading
import asyncio
import json
import time
import numpy as np
import pyaudio
import queue
from openwakeword.model import Model
from google import genai
from google.genai import types

WAKEWORD = "hey_jarvis"
NORMAL_THRESHOLD = 0.5
CONV_THRESHOLD = 0.1
CONV_DURATION = 300
SAMPLE_RATE = 16000
CHUNK = 1280
LIVE_MODEL = "gemini-3.1-flash-live-preview"

class VoiceListener:
    def __init__(self, bot, show_bubble_func):
        self.bot = bot
        self.show_bubble = show_bubble_func
        self.oww_model = Model(wakeword_models=[WAKEWORD], inference_framework="onnx")
        self._running = False
        self._listening = False
        self.last_interaction_time = 0
        self.api_key = ""
        try:
            with open("config.json", "r") as f:
                self.api_key = json.load(f).get("gemini_api_key", "")
        except Exception: pass

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
        stream = pa.open(rate=SAMPLE_RATE, channels=1, format=pyaudio.paInt16, input=True, frames_per_buffer=CHUNK)
        try:
            while self._running:
                raw = stream.read(CHUNK, exception_on_overflow=False)
                audio = np.frombuffer(raw, dtype=np.int16)
                if self._listening: continue
                prediction = self.oww_model.predict(audio)
                score = prediction.get(WAKEWORD, 0)
                current_time = time.time()
                in_conv = (current_time - self.last_interaction_time) < CONV_DURATION
                active_threshold = CONV_THRESHOLD if in_conv else NORMAL_THRESHOLD
                if score >= active_threshold:
                    print(f"\n✅ 자비스 호출 감지! (점수: {score:.2f})")
                    self.oww_model.reset()
                    self._listening = True
                    asyncio.run(self._live_api_session(stream, pa))
                    self.last_interaction_time = time.time()
                    self._listening = False
        finally:
            stream.stop_stream(); stream.close(); pa.terminate()

    async def _live_api_session(self, stream, pa):
        if not self.api_key: return
        client = genai.Client(api_key=self.api_key)
        
        # 💡 [업그레이드] 알람과 글자 찾기(find) 파라미터가 추가된 도구 스키마
        robot_tool = {
            "function_declarations": [
                {
                    "name": "execute_robot_command",
                    "description": "자비스 로봇의 UI 기능(타이머, 알람, 화면 캡처, 날씨, 주식, 달력, 폴더, 글자 찾기, 가이드)을 실행합니다.",
                    "parameters": {
                        "type": "OBJECT",
                        "properties": {
                            "action": {
                                "type": "STRING",
                                "description": "명령 종류: 'timer', 'alarm', 'screenshot', 'weather', 'stock', 'todo', 'folder', 'guide', 'find'"
                            },
                            "minutes": {
                                "type": "INTEGER",
                                "description": "타이머를 설정할 때의 분(minute) 단위 시간"
                            },
                            "alarm_time": {
                                "type": "STRING",
                                "description": "알람을 설정할 때의 시간 (반드시 'HH:MM' 형식, 예: '08:30', '14:00')"
                            },
                            "target_word": {
                                "type": "STRING",
                                "description": "화면에서 찾을 특정 글자나 단어"
                            }
                        },
                        "required": ["action"]
                    }
                }
            ]
        }

        # 💡 시스템 지침에 알람과 글자 찾기 사용법 명시
        config = types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            tools=[robot_tool],
            system_instruction=(
                "너는 AI 비서 자비스야. 짧고 명확하게 한국어로 대답해줘. "
                "사용자가 타이머, 알람, 화면 캡처, 날씨, 주식, 일정(달력), 폴더 열기, 가이드, 또는 화면에서 특정 글자 찾기를 요구하면, "
                "말로 대답하는 것과 동시에 반드시 'execute_robot_command' 도구를 호출해서 기능을 실행시켜. "
                "알람 설정 시 시간(HH:MM)을 'alarm_time' 파라미터로 넘겨주고, 글자 찾기 요구 시 찾을 단어를 'target_word' 파라미터로 넘겨줘."
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
                    while self._listening:
                        raw = await asyncio.to_thread(stream.read, CHUNK, exception_on_overflow=False)
                        audio_arr = np.frombuffer(raw, dtype=np.int16).astype(np.float32)
                        rms = int(np.sqrt(np.mean(audio_arr ** 2)))
                        level = min(rms // 150, 20)
                        bar = "█" * level + "░" * (20 - level)
                        print(f"\r🎤 |{bar}| ", end="", flush=True)
                        await session.send_realtime_input(audio=types.Blob(data=raw, mime_type=f"audio/pcm;rate={SAMPLE_RATE}"))
                
                send_task = asyncio.create_task(send_mic())
                
                async for response in session.receive():
                    # 툴 호출(명령) 감지
                    if response.tool_call:
                        for fc in response.tool_call.function_calls:
                            if fc.name == "execute_robot_command":
                                args = dict(fc.args) if fc.args else {}
                                print(f"\n⚡ [도구 호출 감지] 명령 실행: {args}")
                                handle_voice_command(args, self.bot, self.show_bubble)

                    # 오디오 출력 처리
                    if response.server_content and response.server_content.model_turn:
                        for part in response.server_content.model_turn.parts:
                            if part.inline_data: 
                                play_queue.put(part.inline_data.data)
                                
                    if response.server_content and response.server_content.turn_complete:
                        while not play_queue.empty(): await asyncio.sleep(0.1)
                        await asyncio.sleep(0.6); break
                        
                send_task.cancel()
        except Exception as e: print(f"\n❌ 세션 오류: {e}")
        finally:
            play_queue.put(None); play_thread.join(); audio_out.close()
            print("\n👌 대화 완료!")

# ---------------------------------------------------------
# 🎮 명령 실행 핸들러 (로봇 연동)
# ---------------------------------------------------------
def handle_voice_command(result, bot, show_bubble_func):
    action = result.get("action", "unknown")

    if action == "timer":
        minutes = int(result.get("minutes", 5))
        bot.start_timer(minutes)
        show_bubble_func(f"⏳ {minutes}분 타이머를 시작합니다.", "ALARM", 3000)

    elif action == "alarm":
        # 💡 [신규] 팝업창 없이 즉시 알람 설정
        alarm_time = result.get("alarm_time")
        if alarm_time:
            bot.timer_alarm.target_alarm_time = alarm_time
            show_bubble_func(f"⏰ 오늘 {alarm_time}에 알람이 설정되었습니다!", "ALARM", 3000, True)
        else:
            bot.set_alarm() # 시간이 없으면 기존 팝업창 띄우기

    elif action == "find":
        # 💡 [신규] OCR 글자 추적 즉시 실행
        target_word = result.get("target_word")
        if target_word:
            bot.start_tracking_target_by_word(target_word)
        else:
            bot.start_guide_mode()

    elif action == "screenshot":
        bot.start_screenshot()

    elif action == "weather":
        bot._on_weather_click(None)

    elif action == "stock":
        bot.toggle_stock_bubbles()

    elif action == "todo":
        bot.toggle_todo_bubbles()

    elif action == "folder":
        bot.toggle_folder_bubbles()

    elif action == "guide":
        bot.start_guide_mode()