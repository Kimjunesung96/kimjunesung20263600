from fastapi import APIRouter, HTTPException
from core.database import get_db_connection

router = APIRouter(prefix="/api")

@router.get("/news")
def get_all_news(limit: int = 10, offset: int = 0):
    """모든 뉴스를 최신순으로 조회합니다 (무한 스크롤 지원)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, category_code, title, url, ai_summary, created_at FROM news "
        "ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (limit, offset)
    )
    data = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"status": "success", "data": data}

@router.get("/news/{category_code}")
def get_news_by_category(category_code: str, limit: int = 10, offset: int = 0):
    """특정 카테고리의 뉴스를 조회합니다."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, category_code, title, url, ai_summary, created_at FROM news "
            "WHERE category_code = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (category_code, limit, offset)
        )
        return {"status": "success", "data": [dict(row) for row in cursor.fetchall()]}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

@router.get("/search")
def search_news(q: str = "", keyword: str = "", limit: int = 10, offset: int = 0):
    """제목이나 요약 내용에서 키워드로 뉴스를 검색합니다."""
    search_term = q or keyword
    if not search_term:
        return {"status": "error", "message": "검색어를 입력하세요"}
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        term = f"%{search_term}%"
        cursor.execute(
            "SELECT id, category_code, title, url, ai_summary, created_at FROM news "
            "WHERE title LIKE ? OR ai_summary LIKE ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (term, term, limit, offset)
        )
        return {"status": "success", "data": [dict(row) for row in cursor.fetchall()]}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()