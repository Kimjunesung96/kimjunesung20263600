import tkinter as tk

class FaceFeature:
    def __init__(self, root, face_label):
        self.root = root
        self.face_label = face_label
        
        # 💡 표정 사전: 여기서 모든 표정과 폰트 크기를 한 번에 관리합니다.
        self.faces = {
            "idle":      {"text": "🤖", "size": 45},
            "listening": {"text": "( ⦿_⦿ )", "size": 35},
            "thinking":  {"text": "( @ㅁ@ )", "size": 35},
            "speaking":  {"text": "( ^▽^ )", "size": 35}
        }

    def set_state(self, state):
        """주어진 상태에 맞춰 표정을 변경합니다."""
        if state in self.faces:
            face_data = self.faces[state]
            self.root.after(0, lambda: self.face_label.config(
                text=face_data["text"], 
                font=("Arial", face_data["size"])
            ))