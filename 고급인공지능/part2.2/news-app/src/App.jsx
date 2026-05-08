import { useState, useEffect } from 'react'

function App() {
  const [activeTab, setActiveTab] = useState('01'); 
  const [newsList, setNewsList] = useState([]); 
  const [isLoading, setIsLoading] = useState(false); 
  
  // 💡 하단 메뉴바 이동 상태 (home 또는 settings)
  const [currentMenu, setCurrentMenu] = useState('home');
  // 💡 알람 주기 상태
  const [alarmInterval, setAlarmInterval] = useState(10);

  // 초기 설정값 불러오기
  useEffect(() => {
    fetch("http://localhost:8000/api/settings")
      .then(res => res.json())
      .then(data => setAlarmInterval(data.alarm_interval));
  }, []);

  // 뉴스가져오기 (홈 화면일 때만)
  useEffect(() => {
    if (currentMenu !== 'home') return;
    setIsLoading(true); 
    fetch(`http://localhost:8000/api/news/${activeTab}`)
      .then(response => response.json())
      .then(result => {
        if (result.status === "success") setNewsList(result.data);
        setIsLoading(false); 
      })
      .catch(error => {
        console.error("실패:", error);
        setIsLoading(false);
      });
  }, [activeTab, currentMenu]); 

  const openNewsLink = (url) => window.open(url, '_blank'); 

  // 💡 알람 주기 저장 함수
  const saveSettings = (val) => {
    setAlarmInterval(val);
    fetch("http://localhost:8000/api/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ alarm_interval: val })
    }).then(() => alert(`✅ 로봇 알람 주기가 ${val}분으로 변경되었습니다!`));
  };

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', border: '1px solid #ddd', height: '100vh', display: 'flex', flexDirection: 'column', fontFamily: 'sans-serif' }}>
      
      <header style={{ padding: '20px', backgroundColor: '#202124', color: 'white', textAlign: 'center', fontSize: '1.2rem', fontWeight: 'bold' }}>
        AI 뉴스 큐레이터
      </header>

      {/* 💡 홈 화면일 때 */}
      {currentMenu === 'home' ? (
        <>
          <div style={{ display: 'flex', borderBottom: '1px solid #ddd' }}>
            <button onClick={() => setActiveTab('01')} style={{ flex: 1, padding: '15px', border: 'none', backgroundColor: activeTab === '01' ? '#e8f0fe' : 'white', cursor: 'pointer', fontWeight: activeTab === '01' ? 'bold' : 'normal', color: activeTab === '01' ? '#1a73e8' : '#555' }}>IT/테크</button>
            <button onClick={() => setActiveTab('02')} style={{ flex: 1, padding: '15px', border: 'none', backgroundColor: activeTab === '02' ? '#e8f0fe' : 'white', cursor: 'pointer', fontWeight: activeTab === '02' ? 'bold' : 'normal', color: activeTab === '02' ? '#1a73e8' : '#555' }}>경제</button>
            <button onClick={() => setActiveTab('03')} style={{ flex: 1, padding: '15px', border: 'none', backgroundColor: activeTab === '03' ? '#e8f0fe' : 'white', cursor: 'pointer', fontWeight: activeTab === '03' ? 'bold' : 'normal', color: activeTab === '03' ? '#1a73e8' : '#555' }}>사회</button>
          </div>
          <div style={{ flex: 1, overflowY: 'auto', padding: '15px', backgroundColor: '#f0f2f5' }}>
            {isLoading ? (
              <div style={{ textAlign: 'center', marginTop: '50px', color: '#888', fontWeight: 'bold' }}>뉴스를 불러오는 중입니다... 📡</div>
            ) : (
              newsList.length > 0 ? (
                newsList.map(news => (
                  <div key={news.id} onClick={() => openNewsLink(news.url)} style={{ backgroundColor: 'white', padding: '20px', borderRadius: '15px', marginBottom: '15px', boxShadow: '0 2px 5px rgba(0,0,0,0.05)', cursor: 'pointer' }}>
                    <div style={{ fontSize: '0.8rem', color: '#1a73e8', fontWeight: 'bold', marginBottom: '8px' }}>{news.created_at}</div>
                    <div style={{ fontWeight: 'bold', fontSize: '1.15rem', marginBottom: '10px', color: '#202124', wordBreak: 'keep-all' }}>{news.title}</div>
                    <div style={{ fontSize: '0.95rem', color: '#5f6368', lineHeight: '1.5' }}>{news.ai_summary.replace(/&nbsp;/g, ' ')}</div>
                  </div>
                ))
              ) : <div style={{ textAlign: 'center', marginTop: '50px', color: '#888' }}>이 분야의 뉴스가 아직 없습니다.</div>
            )}
          </div>
        </>
      ) : (
        /* 💡 설정 화면일 때 */
        <div style={{ flex: 1, padding: '30px', backgroundColor: '#f0f2f5' }}>
           <h2 style={{ color: '#202124', marginBottom: '20px' }}>⚙️ 로봇 비서 설정</h2>
           <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '15px', boxShadow: '0 2px 5px rgba(0,0,0,0.05)' }}>
             <p style={{ fontWeight: 'bold', marginBottom: '10px' }}>알람 브리핑 주기</p>
             <select value={alarmInterval} onChange={(e) => saveSettings(e.target.value)} style={{ padding: '10px', width: '100%', borderRadius: '8px', border: '1px solid #ddd', fontSize: '1rem' }}>
               <option value={1}>1분마다 (테스트용)</option>
               <option value={5}>5분마다</option>
               <option value={10}>10분마다 (기본)</option>
               <option value={30}>30분마다</option>
               <option value={60}>1시간마다</option>
             </select>
             <p style={{ fontSize: '0.85rem', color: '#888', marginTop: '15px' }}>* 설정된 주기는 바탕화면 로봇 비서에게 즉시 연동됩니다.</p>
           </div>
        </div>
      )}

      {/* 💡 하단 메뉴 네비게이션 연동 */}
      <div style={{ display: 'flex', borderTop: '1px solid #ddd', backgroundColor: 'white' }}>
        <div onClick={() => setCurrentMenu('home')} style={{ flex: 1, textAlign: 'center', padding: '15px', color: currentMenu === 'home' ? '#1a73e8' : '#9aa0a6', fontWeight: currentMenu === 'home' ? 'bold' : 'normal', cursor: 'pointer' }}>🏠 홈</div>
        <div style={{ flex: 1, textAlign: 'center', padding: '15px', color: '#9aa0a6' }}>📨 브리핑</div>
        <div onClick={() => setCurrentMenu('settings')} style={{ flex: 1, textAlign: 'center', padding: '15px', color: currentMenu === 'settings' ? '#1a73e8' : '#9aa0a6', fontWeight: currentMenu === 'settings' ? 'bold' : 'normal', cursor: 'pointer' }}>⚙️ 설정</div>
      </div>
      
    </div>
  )
}

export default App