import React, { useState, useEffect } from 'react';

export default function Clipboard() {
  const [items, setItems] = useState([]);
  const [selectedImage, setSelectedImage] = useState(null); // 💡 크게 볼 이미지 저장

  // 💡 DB에서 클립보드 내역 가져오기
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

  // 💡 [핵심] 이미지를 다시 클립보드에 복사하는 기능
  const copyImageToClipboard = async (base64Data) => {
    try {
      const response = await fetch(base64Data);
      const blob = await response.blob();
      await navigator.clipboard.write([
        new ClipboardItem({
          [blob.type]: blob
        })
      ]);
      alert("✅ 이미지가 클립보드에 복사되었습니다!\n(카톡이나 그림판에 Ctrl+V 해보세요)");
      setSelectedImage(null); // 복사 후 팝업 닫기
    } catch (err) {
      console.error(err);
      alert("❌ 복사에 실패했습니다.");
    }
  };

  return (
    <div style={{ padding: '20px', backgroundColor: 'white', minHeight: '100vh', position: 'relative' }}>
      
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2 style={{ margin: 0, fontSize: '20px', fontWeight: 'bold', color: '#1a73e8' }}>📋 클립보드 갤러리</h2>
        <button onClick={fetchClipboard} style={{ padding: '5px 10px', backgroundColor: '#f1f3f4', border: '1px solid #ddd', borderRadius: '5px', cursor: 'pointer', fontSize: '12px' }}>
          🔄 새로고침
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '15px' }}>
        
        {items.length === 0 ? (
          <p style={{ gridColumn: '1 / -1', textAlign: 'center', color: '#999', marginTop: '50px' }}>저장된 캡처본이 없습니다.</p>
        ) : (
          items.map(item => (
            <div key={item.id} style={{ border: '1px solid #eee', borderRadius: '12px', overflow: 'hidden', position: 'relative', boxShadow: '0 4px 6px rgba(0,0,0,0.05)', backgroundColor: '#f8f9fa' }}>
              
              <button 
                onClick={() => handleDelete(item.id)} 
                style={{ position: 'absolute', top: '8px', right: '8px', backgroundColor: 'rgba(234, 67, 53, 0.8)', color: 'white', border: 'none', borderRadius: '50%', width: '24px', height: '24px', cursor: 'pointer', zIndex: 10, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px' }}
              >
                ✖
              </button>

              {item.type === 'image' && (
                <img 
                  src={item.content} 
                  alt="캡처" 
                  style={{ width: '100%', height: '150px', objectFit: 'cover', display: 'block', cursor: 'pointer' }} 
                  onClick={() => setSelectedImage(item.content)} // 💡 누르면 팝업(모달) 띄우기!
                />
              )}

              <div style={{ padding: '8px', backgroundColor: 'white', fontSize: '11px', color: '#5f6368', textAlign: 'center', borderTop: '1px solid #eee' }}>
                {new Date(item.created_at).toLocaleString('ko-KR', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
              </div>
              
            </div>
          ))
        )}

      </div>

      {/* 💡 [신규] 이미지를 크게 보여주고 복사하는 팝업(모달) 창 */}
      {selectedImage && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, 
          backgroundColor: 'rgba(0,0,0,0.85)', zIndex: 9999,
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '20px'
        }}>
          {/* 크게 보이는 이미지 */}
          <img 
            src={selectedImage} 
            alt="원본 캡처" 
            style={{ maxWidth: '100%', maxHeight: '70vh', objectFit: 'contain', borderRadius: '8px', boxShadow: '0 10px 25px rgba(0,0,0,0.5)' }} 
          />
          
          {/* 하단 버튼들 */}
          <div style={{ display: 'flex', gap: '15px', marginTop: '25px' }}>
            <button 
              onClick={() => copyImageToClipboard(selectedImage)}
              style={{ padding: '12px 24px', backgroundColor: '#1a73e8', color: 'white', border: 'none', borderRadius: '30px', fontSize: '16px', fontWeight: 'bold', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', boxShadow: '0 4px 6px rgba(0,0,0,0.2)' }}
            >
              📋 복사하기
            </button>
            <button 
              onClick={() => setSelectedImage(null)}
              style={{ padding: '12px 24px', backgroundColor: '#5f6368', color: 'white', border: 'none', borderRadius: '30px', fontSize: '16px', fontWeight: 'bold', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', boxShadow: '0 4px 6px rgba(0,0,0,0.2)' }}
            >
              ✖ 닫기
            </button>
          </div>
        </div>
      )}

    </div>
  );
}