import React, { useState, useEffect } from 'react';

export default function Clipboard() {
  const [items, setItems] = useState([]);

  // 💡 DB에서 클립보드 내역(이미지) 가져오기
  const fetchClipboard = () => {
    fetch('http://localhost:8000/api/clipboard')
      .then(res => res.json())
      .then(data => {
        if(data.status === 'success') setItems(data.data);
      })
      .catch(err => console.error("클립보드 불러오기 실패:", err));
  };

  useEffect(() => {
    fetchClipboard();
  }, []);

  // 💡 이미지 삭제 기능
  const handleDelete = (id) => {
    if(window.confirm("이 캡처본을 삭제하시겠습니까?")) {
      fetch(`http://localhost:8000/api/clipboard/${id}`, { method: 'DELETE' })
        .then(() => fetchClipboard());
    }
  };

  return (
    <div style={{ padding: '20px', backgroundColor: 'white', minHeight: '100vh' }}>
      
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2 style={{ margin: 0, fontSize: '20px', fontWeight: 'bold', color: '#1a73e8' }}>📋 클립보드 갤러리</h2>
        <button onClick={fetchClipboard} style={{ padding: '5px 10px', backgroundColor: '#f1f3f4', border: '1px solid #ddd', borderRadius: '5px', cursor: 'pointer', fontSize: '12px' }}>
          🔄 새로고침
        </button>
      </div>

      {/* 💡 인스타그램 스타일 격자(Grid) 배열 */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '15px' }}>
        
        {items.length === 0 ? (
          <p style={{ gridColumn: '1 / -1', textAlign: 'center', color: '#999', marginTop: '50px' }}>저장된 캡처본이 없습니다.</p>
        ) : (
          items.map(item => (
            <div key={item.id} style={{ border: '1px solid #eee', borderRadius: '12px', overflow: 'hidden', position: 'relative', boxShadow: '0 4px 6px rgba(0,0,0,0.05)', backgroundColor: '#f8f9fa' }}>
              
              {/* 삭제 버튼 (우측 상단 둥둥) */}
              <button 
                onClick={() => handleDelete(item.id)} 
                style={{ position: 'absolute', top: '8px', right: '8px', backgroundColor: 'rgba(234, 67, 53, 0.8)', color: 'white', border: 'none', borderRadius: '50%', width: '24px', height: '24px', cursor: 'pointer', zIndex: 10, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px' }}
              >
                ✖
              </button>

              {/* 이미지 렌더링 (Base64 데이터) */}
              {item.type === 'image' && (
                <img 
                  src={item.content} 
                  alt="캡처" 
                  style={{ width: '100%', height: '150px', objectFit: 'cover', display: 'block', cursor: 'pointer' }} 
                  onClick={() => window.open(item.content)} // 누르면 원본 크기로 보기
                />
              )}

              {/* 캡처된 시간 표시 */}
              <div style={{ padding: '8px', backgroundColor: 'white', fontSize: '11px', color: '#5f6368', textAlign: 'center', borderTop: '1px solid #eee' }}>
                {new Date(item.created_at).toLocaleString('ko-KR', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
              </div>
              
            </div>
          ))
        )}

      </div>
    </div>
  );
}