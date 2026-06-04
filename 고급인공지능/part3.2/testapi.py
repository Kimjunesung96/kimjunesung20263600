import numpy as np
import pyaudio
import asyncio
import json
import threading
import queue
import time
from openwakeword.model import Model
from google import genai
from google.genai import types

# 설정 상수
WAKEWORD    = "hey_jarvis"
NORMAL_THRESHOLD = 0.5  # 평상시 깨우기 점수
CONV_THRESHOLD   = 0.1  # 대화 모드 시 점수 (더 민감하게)
CONV_DURATION    = 300  # 대화 모드 유지 시간 (5분 = 300초)
SAMPLE_RATE = 16000
CHUNK       = 1280
LIVE_MODEL  = "gemini-3.1-flash-live-preview"

# API 키 로드
api_key = ""
try:
    with open("config.json", "r") as f:
        api_key = json.load(f).get("gemini_api_key", "")
except Exception:
    pass

if not api_key:
    print("❌ config.json에 gemini_api_key가 없습니다!")
    exit()

print("🎤 자비스 스마트 대화 시스템 가동!")
print(f"   기본 문턱값: {NORMAL_THRESHOLD} -> 대화 모드 활성화 시: {CONV_THRESHOLD}")
print("-" * 50)

oww_model = Model(wakeword_models=[WAKEWORD], inference_framework="onnx")

# ── 오디오 재생 백그라운드 스레드 워커 ─────────────────────────────────
def audio_play_worker(play_queue, audio_out):
    while True:
        data = play_queue.get()
        if data is None:
            break
        try:
            audio_out.write(data)
        except Exception:
            pass
        play_queue.task_done()


async def run_live_chat_session(stream, pa):
    print(f"\n🔌 [{LIVE_MODEL}] 세션 연결 시도...")
    client = genai.Client(api_key=api_key)

    config = types.LiveConnectConfig(
        response_modalities=["AUDIO"],
        system_instruction=(
            "너는 사용자의 인공지능 비서 자비스야. 친절하고 장황하지 않게 핵심만 짧게 한국어로 대답해줘. "
            "사용자가 '바이바이', '잘 가', '종료'라고 말하면 반드시 대답에 '안녕히 계세요' 또는 '종료합니다'라는 문구를 포함해줘."
        )
    )

    audio_out = pa.open(rate=24000, channels=1, format=pyaudio.paInt16, output=True)
    
    play_queue = queue.Queue()
    play_thread = threading.Thread(target=audio_play_worker, args=(play_queue, audio_out), daemon=True)
    play_thread.start()

    # 마이크 잔여 버퍼 비우기 (이전 대화 소음 제거)
    try:
        available = stream.get_read_available()
        if available > 0:
            stream.read(available, exception_on_overflow=False)
    except Exception:
        pass

    session_active  = True
    jarvis_speaking = False

    try:
        async with client.aio.live.connect(model=LIVE_MODEL, config=config) as session:
            print("✅ 자비스 연결 성공! 말씀하세요...")

            # ── 1. 송신 태스크 ───────────────────────────────────────────
            async def send_mic_audio():
                nonlocal session_active, jarvis_speaking
                try:
                    while session_active:
                        raw = await asyncio.to_thread(
                            stream.read, CHUNK, exception_on_overflow=False
                        )
                        if not session_active:
                            break

                        if jarvis_speaking:
                            await asyncio.sleep(0.01)
                            continue

                        # VU 미터 출력
                        audio_arr = np.frombuffer(raw, dtype=np.int16).astype(np.float32)
                        rms   = int(np.sqrt(np.mean(audio_arr ** 2)))
                        level = min(rms // 150, 20)
                        bar   = "█" * level + "░" * (20 - level)
                        print(f"\r🎤 |{bar}| ", end="", flush=True)

                        await session.send_realtime_input(
                            audio=types.Blob(data=raw, mime_type=f"audio/pcm;rate={SAMPLE_RATE}")
                        )
                        await asyncio.sleep(0.001)

                except asyncio.CancelledError:
                    pass
                except Exception:
                    session_active = False

            # ── 2. 수신 태스크 ───────────────────────────────────────────
            async def receive_jarvis_voice():
                nonlocal session_active, jarvis_speaking
                try:
                    async for response in session.receive():
                        if not session_active:
                            break

                        if response.server_content is None:
                            continue

                        if response.server_content.model_turn:
                            if not jarvis_speaking:
                                jarvis_speaking = True
                                print("\n🔊 자비스: ", end="", flush=True)

                            for part in response.server_content.model_turn.parts:
                                if part.text:
                                    print(part.text, end="", flush=True)
                                    if any(w in part.text for w in ["안녕히 계세요", "종료합니다", "바이바이"]):
                                        print("\n👋 종료 키워드 감지")
                                        session_active = False

                                if part.inline_data and part.inline_data.data:
                                    play_queue.put(part.inline_data.data)

                        # 🔥 [핵심] 자비스의 한 턴 답변이 완전히 끝나면 세션을 종료합니다.
                        if response.server_content.turn_complete:
                            # 큐에 쌓인 오디오가 다 재생될 때까지 잠시 대기
                            while not play_queue.empty():
                                await asyncio.sleep(0.1)
                            await asyncio.sleep(0.6)  # 마지막 청크 재생 마진
                            
                            jarvis_speaking = False
                            session_active = False  # 타임아웃 방지를 위해 루프 탈출 (세션 닫기)
                            print("\n\n👌 대화 완료! 세션을 안전하게 닫고 대기 모드로 전환합니다.")

                except asyncio.CancelledError:
                    pass
                except Exception:
                    session_active = False

            send_task    = asyncio.create_task(send_mic_audio())
            receive_task = asyncio.create_task(receive_jarvis_voice())

            while session_active:
                await asyncio.sleep(0.1)

            send_task.cancel()
            receive_task.cancel()
            await asyncio.gather(send_task, receive_task, return_exceptions=True)

    except Exception as e:
        print(f"\n❌ 라이브 세션 오류: {e}")
    finally:
        play_queue.put(None)
        play_thread.join(timeout=1.0)
        audio_out.stop_stream()
        audio_out.close()
        print("🚪 웹소켓 세션이 정상적으로 종료되었습니다.")


async def main():
    pa = pyaudio.PyAudio()
    stream = pa.open(
        rate=SAMPLE_RATE, channels=1,
        format=pyaudio.paInt16,
        input=True, frames_per_buffer=CHUNK
    )

    # 대화 모드 관리를 위한 변수
    last_interaction_time = 0  # 마지막으로 자비스와 대화가 끝난 시간

    print("\n🎤 'Hey Jarvis' 라고 불러서 자비스를 깨워보세요... (종료: Ctrl+C)")

    try:
        while True:
            raw   = await asyncio.to_thread(stream.read, CHUNK, exception_on_overflow=False)
            audio = np.frombuffer(raw, dtype=np.int16)

            prediction = oww_model.predict(audio)
            score      = prediction.get(WAKEWORD, 0)

            # 🔥 [핵심] 현재 시간이 마지막 대화 종료 후 5분 이내인지 체크
            current_time = time.time()
            in_conversation_mode = (current_time - last_interaction_time) < CONV_DURATION
            
            # 대화 모드에 따라 유동적으로 감지 문턱값 설정
            active_threshold = CONV_THRESHOLD if in_conversation_mode else NORMAL_THRESHOLD

            if score > 0.05:
                mode_str = "🔥 대화모드(민감)" if in_conversation_mode else "💤 일반모드"
                bar = "█" * int(score * 20)
                print(f"\r   [{mode_str}] 감지율: {score:.3f} |{bar:<20}| [목표: {active_threshold}]", end="", flush=True)

            if score >= active_threshold:
                print(f"\n\n🔊 자비스 호출 감지! (점수: {score:.3f})")
                oww_model.reset()
                
                # 대화 세션 진입 (한 턴만 수행하고 나옴)
                await run_live_chat_session(stream, pa)
                
                # 대화가 끝난 시점의 타임스탬프 갱신 -> 이때부터 다시 5분 카운트다운 시작
                last_interaction_time = time.time()
                print(f"\n🎤 다음 대기 중... (5분간 민감도 {CONV_THRESHOLD} 유지)")

    except KeyboardInterrupt:
        print("\n테스트 종료!")
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()


if __name__ == "__main__":
    asyncio.run(main())