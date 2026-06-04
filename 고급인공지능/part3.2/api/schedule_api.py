from fastapi import APIRouter
from pydantic import BaseModel
from core.database import get_db_connection

router = APIRouter(prefix="/api")

class ScheduleItem(BaseModel):
    date: str
    content: str

class ClipboardItem(BaseModel):
    type: str
    content: str

@router.get("/schedule/{date}")
def get_schedule(date: str):
    """특정 날짜의 일정을 조회합니다."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, content FROM schedule WHERE date = ? ORDER BY id ASC", (date,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"status": "success", "data": rows}

@router.post("/schedule")
def add_schedule(item: ScheduleItem):
    """새로운 일정을 등록합니다."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO schedule (date, content) VALUES (?, ?)", (item.date, item.content))
    conn.commit()
    conn.close()
    return {"status": "success"}

@router.delete("/schedule/{id}")
def delete_schedule(id: int):
    """일정을 삭제합니다."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM schedule WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"status": "success"}

@router.get("/clipboard")
def get_clipboard():
    """최근 20개의 클립보드 내역을 가져옵니다."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, type, content, created_at FROM clipboard ORDER BY created_at DESC LIMIT 20")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"status": "success", "data": rows}

@router.post("/clipboard")
def add_clipboard(item: ClipboardItem):
    """클립보드 내용을 추가합니다 (이미지 포함)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clipboard (type, content) VALUES (?, ?)", (item.type, item.content))
    conn.commit()
    conn.close()
    return {"status": "success"}