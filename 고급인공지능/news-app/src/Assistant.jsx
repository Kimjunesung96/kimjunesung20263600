import { useState, useEffect } from 'react';

export default function Assistant({ newsData }) {
  const [bubbles, setBubbles] = useState([]); 
  const [isTalking, setIsTalking] = useState(false); 
  const [settings] = useState({
    maxBubbles: 3,       
    displayTime: 5000,   
  });

  useEffect(() => {
    if (!newsData || newsData.length === 0) return;

    const latestNews = newsData;
    const newBubble = { id: Date.now(), text: latestNews.title };

    setBubbles(prev => {
      const newList = [...prev, newBubble];
      if (newList.length > settings.maxBubbles) return newList.slice(newList.length - settings.maxBubbles);
      return newList;
    });

    setIsTalking(true);

    const timer = setTimeout(() => {
      setBubbles(prev => prev.filter(b => b.id !== newBubble.id));
      setIsTalking(false); 
    }, settings.displayTime);

    return () => clearTimeout(timer); 
  }, [newsData, settings]); 

  return (
    <div style={{
      position: 'fixed', bottom: '30px', right: '30px', zIndex: 9999,
      display: 'flex', flexDirection: 'column', alignItems: 'flex-end', transition: 'all 0.5s'
    }}>
      {/* 1. 말풍선 렌더링 영역 */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '15px' }}>
        {bubbles.map(b => (
          <div key={b.id} style={{
            backgroundColor: 'white', border: '3px solid #1a73e8', color: '#202124',
            padding: '12px', borderRadius: '20px', maxWidth: '250px',
            boxShadow: '0 4px 10px rgba(0,0,0,0.15)', fontSize: '0.9rem', fontWeight: 'bold'
          }}>
            💬 {b.text}
          </div>
        ))}
      </div>

      {/* 2. 비서 얼굴 영역 (애니메이션) */}
      <div style={{
        position: 'relative', width: '80px', height: '80px',
        backgroundColor: '#e8f0fe', borderRadius: '50%',
        border: '4px solid #1a73e8', boxShadow: '0 5px 15px rgba(0,0,0,0.2)',
        display: 'flex', justifyContent: 'center', alignItems: 'center'
      }}>
        {/* 눈 */}
        <div style={{ position: 'absolute', top: '22px', display: 'flex', gap: '16px' }}>
          <div style={{ width: '10px', height: '10px', backgroundColor: '#202124', borderRadius: '50%' }}></div>
          <div style={{ width: '10px', height: '10px', backgroundColor: '#202124', borderRadius: '50%' }}></div>
        </div>
        {/* 뻐끔거리는 입 */}
        <div style={{
          position: 'absolute', bottom: '20px', backgroundColor: '#ea4335',
          transition: 'all 0.15s',
          width: isTalking ? '20px' : '20px',
          height: isTalking ? '20px' : '6px',
          borderRadius: isTalking ? '50%' : '5px'
        }}></div>
      </div>
    </div>
  );
}