import time

class BotEventHandler:
    def __init__(self, root, face_label, bot_instance):
        self.root = root
        self.face_label = face_label
        self.bot = bot_instance
        self.last_toggle_time = 0

    def on_press(self, event):
        """마우스 클릭 시작 시 현재 좌표를 저장합니다."""
        if event.num == 3: return # 우클릭 제외
        self.face_label._drag_start_x = event.x
        self.face_label._drag_start_y = event.y
        self.face_label._is_dragging = False

    def on_drag(self, event, close_menus_callback):
        """드래그 시 로봇을 이동시키고 열려있는 모든 서브 메뉴를 닫습니다."""
        dx, dy = abs(event.x - self.face_label._drag_start_x), abs(event.y - self.face_label._drag_start_y)
        
        # 5픽셀 이상 움직였을 때만 드래그로 간주
        if dx > 5 or dy > 5:
            if not getattr(self.face_label, '_is_dragging', False):
                close_menus_callback() # 메인 파일의 메뉴 닫기 함수 호출
                self.face_label._is_dragging = True
            
            # 새 좌표 계산 및 윈도우 이동
            new_x = self.root.winfo_x() - self.face_label._drag_start_x + event.x
            new_y = self.root.winfo_y() - self.face_label._drag_start_y + event.y
            self.root.geometry(f"+{new_x}+{new_y}")
            
            # 따라다니는 기능들(주식, 일정 등)의 위치도 업데이트
            if hasattr(self.bot, 'update_todo_position'): self.bot.update_todo_position()
            if hasattr(self.bot, 'update_folder_position'): self.bot.update_folder_position()
            if hasattr(self.bot, 'update_stock_position'): self.bot.update_stock_position()