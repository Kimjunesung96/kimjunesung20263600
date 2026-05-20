import tkinter as tk
from PIL import Image, ImageDraw, ImageFont, ImageGrab
import numpy as np
import cv2
import time
import ctypes

# 💡 [핵심 최적화] 파이썬과 윈도우의 해상도 눈높이를 물리 픽셀(1:1)로 강제 고정합니다!
# 이렇게 하면 화면을 축소할 필요도 없고, 좌표도 100% 완벽하게 일치합니다.
try:
    ctypes.windll.user32.SetProcessDPIAware()
except:
    pass

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
    # 💡 3초 타이머(box_win.after) 삭제! 
    # 대신 빨간 박스나 글씨를 마우스로 [클릭]하면 박스가 꺼지게 만듭니다.
    box_win.bind("<Button-1>", lambda e: box_win.destroy())
    canvas.bind("<Button-1>", lambda e: box_win.destroy())
    box_win.mainloop()

def create_text_template(text, font_size=15):
    try:
        font = ImageFont.truetype("malgun.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    bbox = font.getbbox(text)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    
    # 💡 바탕화면 어두운 배경 + 흰색 글씨 기준 (색상 반전 유지)
    img = Image.new('L', (w + 4, h + 4), color=0)
    draw = ImageDraw.Draw(img)
    draw.text((2, 2), text, font=font, fill=255)
    return np.array(img)

def main():
    target_word = "시이이이작" 
    print(f"⚡ 광속 서치 모드 가동: '{target_word}' 글씨를 찾습니다...")
    
    start_time = time.time()
    
    # 💡 좌표 보정(Resize) 로직 싹 삭제! 원본 픽셀 100% 그대로 씁니다.
    screen_img = ImageGrab.grab().convert('L')
    screen = np.array(screen_img)
    
    base_template = create_text_template(target_word, font_size=15)
    
    best_match_val = -1
    best_loc = None
    best_w, best_h = 0, 0
    
    scales = np.linspace(0.5, 2.0, 15)
    for scale in scales:
        w = int(base_template.shape[1] * scale)
        h = int(base_template.shape[0] * scale)
        if w < 5 or h < 5: continue
            
        resized_template = cv2.resize(base_template, (w, h))
        res = cv2.matchTemplate(screen, resized_template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        
        if max_val > best_match_val:
            best_match_val = max_val
            best_loc = max_loc
            best_w = w
            best_h = h

    end_time = time.time()
    
    print(f"🏎️ 걸린 시간: {end_time - start_time:.3f}초")
    print(f"📊 제일 높은 일치율({best_match_val*100:.1f}%) 위치에 무조건 박스를 칩니다!")

    x1 , y1 = best_loc [ 0 ] , best_loc [ 1 ]
    draw_red_box(x1, y1, best_w, best_h)

if __name__ == "__main__":
    main()