import tkinter as tk
import threading
import time
import io
import asyncio
from itertools import product
from PIL import ImageGrab


# ---------------------------------------------------------
# 🎯 OCR 타겟 추적 기능
# ---------------------------------------------------------
class OcrFeature:
    def __init__(self, root, show_bubble_func):
        self.root        = root
        self.show_bubble = show_bubble_func

        self.stop_tracking         = False
        self.active_tracking_boxes = []

    # ---------------------------------------------------------
    # 💣 모든 추적 박스 제거 + 루프 중단
    # ---------------------------------------------------------
    def kill_all_tracking(self):
        self.stop_tracking = True
        for box in self.active_tracking_boxes:
            if box.winfo_exists():
                box.destroy()
        self.active_tracking_boxes.clear()

    # ---------------------------------------------------------
    # 공통: 빨간 박스 그리기
    # ---------------------------------------------------------
    def _draw_red_box(self, x, y, w, h, rank, score=None):
        box_win = tk.Toplevel(self.root)
        self.active_tracking_boxes.append(box_win)
        box_win.overrideredirect(True)
        box_win.attributes("-topmost", True)
        box_win.attributes("-transparentcolor", "white")
        pad   = 5
        extra = 20 if score is not None else 0
        box_win.geometry(f"{w+pad*2}x{h+pad*2+extra}+{x-pad}+{y-pad}")
        canvas = tk.Canvas(box_win, bg="white", highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        color = "red" if rank == 1 else "orange"
        lw    = 5   if rank == 1 else 2
        canvas.create_rectangle(pad, pad, w+pad, h+pad, outline=color, width=lw)
        if score is not None:
            canvas.create_text(
                w // 2 + pad, h + pad + 10,
                text=f"{score:.0f}점", fill=color,
                font=("맑은 고딕", 9, "bold")
            )
        box_win.bind("<Button-1>", lambda e: box_win.destroy())
        canvas.bind("<Button-1>",  lambda e: box_win.destroy())

    # ---------------------------------------------------------
    # 공통: Windows OCR 실행
    # ---------------------------------------------------------
    @staticmethod
    async def _run_ocr(pil_img, with_line_idx=False):
        from winrt.windows.media.ocr import OcrEngine
        from winrt.windows.graphics.imaging import BitmapDecoder
        from winrt.windows.storage.streams import InMemoryRandomAccessStream, DataWriter

        buf = io.BytesIO()
        pil_img.save(buf, format="PNG")
        img_bytes = buf.getvalue()

        lang = None
        try:
            for l in OcrEngine.get_available_recognizer_languages():
                if "ko" in l.language_tag.lower():
                    lang = l
                    break
        except Exception:
            pass

        try:
            engine = (OcrEngine.try_create_from_language(lang)
                      if lang else OcrEngine.try_create_from_user_profile_languages())
        except Exception:
            engine = OcrEngine.try_create_from_user_profile_languages()

        if engine is None:
            return []

        stream = InMemoryRandomAccessStream()
        writer = DataWriter(stream)
        writer.write_bytes(img_bytes)
        await writer.store_async()
        writer.detach_stream()
        stream.seek(0)

        decoder = await BitmapDecoder.create_async(stream)
        bitmap  = await decoder.get_software_bitmap_async()
        result  = await engine.recognize_async(bitmap)

        words = []
        for line_idx, line in enumerate(result.lines):
            for word in line.words:
                r = word.bounding_rect
                entry = {
                    "text": word.text,
                    "x": int(r.x), "y": int(r.y),
                    "w": int(r.width), "h": int(r.height),
                }
                if with_line_idx:
                    entry["line_idx"] = line_idx
                words.append(entry)
        return words

    # ---------------------------------------------------------
    # 다단어 추적 (가이드 모드 검색용)
    # ---------------------------------------------------------
    def start_tracking_target_by_word(self, target_text):
        self.show_bubble(f"🔍 [{target_text}]\nWindows OCR 스캔 중...", "ALARM", 2000, True)
        query_words = target_text.split()

        def calc_score(combo):
            line_ids    = [w["line_idx"] for w in combo]
            line_spread = max(line_ids) - min(line_ids)
            if   line_spread == 0: line_score = 60
            elif line_spread == 1: line_score = 40
            elif line_spread == 2: line_score = 20
            else:                  line_score = 0

            ys      = [w["y"] + w["h"] // 2 for w in combo]
            y_score = max(0, 20 - (max(ys) - min(ys)) // 5)

            xs = [w["x"] for w in combo]
            if len(xs) < 2:
                x_score = 20
            else:
                ordered = sum(1 for i in range(len(xs) - 1) if xs[i] <= xs[i + 1])
                x_score = int(20 * ordered / (len(xs) - 1))

            return line_score + y_score + x_score

        def find_best_group(words):
            candidates = []
            for qw in query_words:
                matched = [w for w in words if qw in w["text"] or w["text"] in qw]
                if not matched:
                    return None, 0
                candidates.append(matched[:3])
            best_score, best_group = -1, None
            for combo in product(*candidates):
                score = calc_score(list(combo))
                if score > best_score:
                    best_score = score
                    best_group = list(combo)
            return best_group, best_score

        def get_bounding_box(group):
            xs  = [w["x"]           for w in group]
            ys  = [w["y"]           for w in group]
            x2s = [w["x"] + w["w"] for w in group]
            y2s = [w["y"] + w["h"] for w in group]
            return min(xs), min(ys), max(x2s) - min(xs), max(y2s) - min(ys)

        def loop():
            self.stop_tracking = False
            while not self.stop_tracking:
                screen_img = ImageGrab.grab()
                try:
                    ev_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(ev_loop)
                    words = ev_loop.run_until_complete(
                        self._run_ocr(screen_img, with_line_idx=True)
                    )
                    ev_loop.close()
                except Exception as e:
                    self.root.after(0, lambda err=str(e): self.show_bubble(
                        f"❌ OCR 오류\n{err[:50]}", "ALARM", 3000, True))
                    return

                if len(query_words) == 1:
                    found, seen = [], set()
                    for word in words:
                        if target_text in word["text"] or word["text"] in target_text:
                            key = (word["x"] // 50, word["y"] // 50)
                            if key not in seen:
                                seen.add(key)
                                found.append(word)
                    if found:
                        for i, word in enumerate(found[:3]):
                            x, y, w, h = word["x"], word["y"], word["w"], word["h"]
                            self.root.after(0, lambda a=x,b=y,c=w,d=h,r=i+1:
                                            self._draw_red_box(a,b,c,d,r))
                            if i == 0:
                                self.root.after(0, lambda wd=word["text"]:
                                    self.show_bubble(f"🎯 [{wd}] 발견!", "ALARM", 3000, True))
                        break
                    else:
                        self.root.after(0, lambda: self.show_bubble(
                            f"😅 [{target_text}] 못 찾음\n다시 시도...", "ALARM", 2000, True))
                        time.sleep(1)
                    continue

                best_group, best_score = find_best_group(words)
                if best_group:
                    bx, by, bw, bh = get_bounding_box(best_group)
                    self.root.after(0, lambda a=bx,b=by,c=bw,d=bh,s=best_score:
                                    self._draw_red_box(a,b,c,d,1,s))
                    self.root.after(0, lambda s=best_score:
                        self.show_bubble(
                            f"🎯 [{target_text}] 발견!\n근접도 점수: {s}점",
                            "ALARM", 3000, True))
                    break
                else:
                    self.root.after(0, lambda: self.show_bubble(
                        f"😅 [{target_text}] 못 찾음\n다시 시도...", "ALARM", 2000, True))
                    time.sleep(1)

        threading.Thread(target=loop, daemon=True).start()

    # ---------------------------------------------------------
    # 텍스트 위젯 선택 기반 추적
    # ---------------------------------------------------------
    def start_tracking_target(self, text_widget):
        try:
            target_text = text_widget.get(tk.SEL_FIRST, tk.SEL_LAST).strip()
        except tk.TclError:
            self.show_bubble("찾을 글자를 먼저 마우스로 긁어주세요!", "ALARM", 3000, True)
            return
        if not target_text:
            return

        self.show_bubble(f"🔍 [{target_text}]\nWindows OCR 스캔 중...", "ALARM", 2000, True)

        def tracking_loop():
            self.stop_tracking = False
            while not self.stop_tracking:
                screen_img = ImageGrab.grab()
                try:
                    ev_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(ev_loop)
                    words = ev_loop.run_until_complete(self._run_ocr(screen_img))
                    ev_loop.close()
                except Exception as e:
                    self.root.after(0, lambda err=str(e): self.show_bubble(
                        f"❌ OCR 오류\n{err[:50]}", "ALARM", 3000, True))
                    return

                found, seen = [], set()
                for word in words:
                    if target_text in word["text"] or word["text"] in target_text:
                        key = (word["x"] // 50, word["y"] // 50)
                        if key not in seen:
                            seen.add(key)
                            found.append(word)

                if found:
                    for i, word in enumerate(found[:3]):
                        x, y, w, h = word["x"], word["y"], word["w"], word["h"]
                        self.root.after(0, lambda a=x,b=y,c=w,d=h,r=i+1:
                                        self._draw_red_box(a,b,c,d,r))
                        if i == 0:
                            self.root.after(0, lambda wd=word["text"]:
                                self.show_bubble(f"🎯 [{wd}] 발견!", "ALARM", 3000, True))
                    break
                else:
                    self.root.after(0, lambda: self.show_bubble(
                        f"😅 [{target_text}] 못 찾음\n다시 시도...", "ALARM", 2000, True))
                    time.sleep(1)

        threading.Thread(target=tracking_loop, daemon=True).start()