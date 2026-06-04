import tkinter as tk
import time
import asyncio
import ctypes
import mss  # 💡 새로운 초고속 캡처 엔진!
from winrt.windows.media.ocr import OcrEngine
from winrt.windows.graphics.imaging import BitmapPixelFormat, SoftwareBitmap
from winrt.windows.globalization import Language
from winrt.windows.storage.streams import DataWriter

# 💡 [핵심 최적화] 파이썬과 윈도우의 해상도 눈높이를 물리 픽셀(1:1)로 강제 고정!
try:
    ctypes.windll.user32.SetProcessDPIAware()
except:
    pass

# 기존 빨간 박스 그리는 함수 (이건 완벽해서 변경 없이 그대로 씁니다)
def draw_red_box(x, y, w, h):
    box_win = tk.Tk()
    box_win.overrideredirect(True)
    box_win.attributes("-topmost", True)
    box_win.attributes("-transparentcolor", "white") 
    
    pad = 5
    box_win.geometry(f"{w + pad*2}x{h + pad*2}+{x - pad}+{y - pad}")
    
    canvas = tk.Canvas(box_win, bg="white", highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    
    def blink(is_visible):
        canvas.delete("all")
        if is_visible:
            canvas.create_rectangle(pad, pad, w + pad, h + pad, outline="red", width=4)
        box_win.after(400, blink, not is_visible)
        
    blink(True)
    box_win.bind("<Button-1>", lambda e: box_win.destroy())
    canvas.bind("<Button-1>", lambda e: box_win.destroy())
    box_win.mainloop()

async def main():
    target_word = "시이이이작" 
    print(f"⚡ WinRT OCR 모드 가동: 화면에서 '{target_word}' 글씨를 읽어냅니다...")
    
    start_time = time.time()
    
    # 1. 💡 화면 캡처: ImageGrab 버리고 초고속 mss로 갈아탑니다!
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # 주 모니터 캡처
        sct_img = sct.grab(monitor)
        width, height = sct_img.width, sct_img.height
        raw_bytes = sct_img.bgra  # 캡처된 생고기 데이터(바이트)
        
    # 2. 💡 WinRT가 좋아하는 포맷으로 데이터 번역 (DataWriter 활용)
    writer = DataWriter()
    writer.write_bytes(bytearray(raw_bytes)) # 파이썬 바이트를 윈도우 바이트로 변환
    buffer = writer.detach_buffer()
    
    # WinRT 전용 비트맵(SoftwareBitmap) 생성
    software_bitmap = SoftwareBitmap.create_copy_from_buffer(buffer, BitmapPixelFormat.BGRA8, width, height)
    
    # 3. 💡 OCR 엔진 초기화 및 인식 (한국어 모드)
    lang = Language("ko-KR")
    engine = OcrEngine.try_create_from_language(lang)
    
    # 윈도우 엔진아, 글씨 좀 읽어와라!
    result = await engine.recognize_async(software_bitmap)
    
    ocr_end_time = time.time()
    print(f"🏎️ 캡처 및 글자 판독 완료: {ocr_end_time - start_time:.3f}초")
    
    # 4. 💡 찾은 글자 좌표 스캔
    found = False
    for line in result.lines:
        if target_word in line.text:
            print(f"✅ 발견된 문장: '{line.text}'")
            
            # 문장 안에서 정확한 단어의 위치만 콕 집어내기
            for word in line.words:
                if target_word in word.text:
                    x = int(word.bounding_rect.x)
                    y = int(word.bounding_rect.y)
                    w = int(word.bounding_rect.width)
                    h = int(word.bounding_rect.height)
                    
                    print(f"🎯 좌표 적중: x={x}, y={y}, w={w}, h={h}")
                    draw_red_box(x, y, w, h)
                    found = True
                    break
        if found: break
            
    if not found:
        print(f"❌ 화면에서 '{target_word}'를 찾을 수 없습니다.")

if __name__ == "__main__":
    asyncio.run(main())