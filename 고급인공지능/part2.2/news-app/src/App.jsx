import { useState, useEffect } from 'react'
import Calendar from './Calendar'; 
import Clipboard from './Clipboard';

const ALL_CATEGORIES = [
  { id: '01', name: 'IT/테크' }, { id: '02', name: '경제' },
  { id: '03', name: '사회' }, { id: '04', name: '세계' },
  { id: '05', name: '연예' }, { id: '06', name: '스포츠' },
  { id: '07', name: '과학' }, { id: '08', name: '건강' },
];

export default function App() {
  const [activeTab, setActiveTab] = useState('01'); 
  const [newsList, setNewsList] = useState([]); 
  const [isLoading, setIsLoading] = useState(false);
  const [currentMenu, setCurrentMenu] = useState('home');
  
  const [alarmInterval, setAlarmInterval] = useState(10);
  const [enabledCategories, setEnabledCategories] = useState(['01', '02', '03']);
  const [bubbleDuration, setBubbleDuration] = useState(5);
  const [newsCount, setNewsCount] = useState(10);

  const [favoriteStocks, setFavoriteStocks] = useState([]);
  const [newStockName, setNewStockName] = useState("");
  const [searchResults, setSearchResults] = useState([]); 

  useEffect(() => {
    fetch("http://localhost:8000/api/settings")
      .then(res => res.json())
      .then(data => {
        if (data.alarm_interval) setAlarmInterval(data.alarm_interval);
        if (data.enabled_categories) setEnabledCategories(data.enabled_categories);
        if (data.bubble_duration !== undefined) setBubbleDuration(data.bubble_duration);
        if (data.news_count !== undefined) setNewsCount(data.news_count);
      });
      
    fetchStocks();
  }, []);

  const fetchStocks = () => {
    fetch("http://localhost:8000/api/favorites")
      .then(res => res.json())
      .then(data => { if(data.status === 'success') setFavoriteStocks(data.data); });
  };

  useEffect(() => {
    if (currentMenu !== 'home') return;
    setIsLoading(true); 
    fetch(`http://localhost:8000/api/news/${activeTab}`)
      .then(response => response.json())
      .then(result => {
        if (result.status === "success") setNewsList(result.data);
        setIsLoading(false); 
      })
      .catch(error => { console.error(error); setIsLoading(false); });
  }, [activeTab, currentMenu]); 

  const openNewsLink = (url) => window.open(url, '_blank');

  const saveAllSettings = (newInterval, newCategories, newDuration, newCount) => {
    fetch("http://localhost:8000/api/settings", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ alarm_interval: newInterval, enabled_categories: newCategories, bubble_duration: parseInt(newDuration) || 0, news_count: parseInt(newCount) || 0 })
    });
  };

  const handleIntervalChange = (val) => { setAlarmInterval(parseInt(val)); saveAllSettings(parseInt(val), enabledCategories, bubbleDuration, newsCount); };
  const handleCategoryToggle = (id) => {
    const next = enabledCategories.includes(id) ? enabledCategories.filter(c => c !== id) : [...enabledCategories, id];
    if (next.length === 0) return;
    setEnabledCategories(next); saveAllSettings(alarmInterval, next, bubbleDuration, newsCount);
  };
  const handleDurationChange = (val) => { setBubbleDuration(val); saveAllSettings(alarmInterval, enabledCategories, val, newsCount); };
  const handleCountChange = (val) => { setNewsCount(val); saveAllSettings(alarmInterval, enabledCategories, bubbleDuration, val); };

  const handleSearchChange = (val) => {
    setNewStockName(val);
    if (!val.trim()) {
      setSearchResults([]);
      return;
    }
    fetch(`http://localhost:8000/api/search_stock?name=${encodeURIComponent(val)}`)
      .then(res => res.json())
      .then(data => { if (data.status === 'success') setSearchResults(data.data); })
      .catch(() => setSearchResults([]));
  };

  // 💡 [핵심] 리액트가 찾은 '티커(stockTicker)'를 파이썬에게 직접 찔러줍니다!
  const handleSelectAndAdd = (stockName, stockTicker) => {
    setNewStockName(""); // 클릭하면 검색창 깔끔하게 비우기!
    setSearchResults([]); 
    handleAddStock(stockName, stockTicker);
  };

  const handleAddStock = (targetName = newStockName, targetTicker = "") => {
    if (!targetName.trim()) return alert("종목명을 입력해주세요!");
    
    const btn = document.getElementById("addStockBtn");
    if(btn) { btn.innerText = "추가 중..."; btn.disabled = true; }

    fetch("http://localhost:8000/api/favorites", {
      method: "POST", headers: { "Content-Type": "application/json" },
      // 티커까지 같이 포장해서 파이썬에 던집니다!
      body: JSON.stringify({ name: targetName.trim(), ticker: targetTicker }) 
    })
    .then(res => res.json())
    .then(data => {
      if(data.status === 'success') { 
          fetchStocks(); 
          setNewStockName(""); 
          setSearchResults([]);
      }
      else alert("❌ " + data.message); // 똑똑해진 에러 메시지 띄우기
    })
    .finally(() => {
        if(btn) { btn.innerText = "추가"; btn.disabled = false; }
    });
  };

  const handleDeleteStock = (id) => {
    if(window.confirm("이 종목을 삭제할까요?")) {
      fetch(`http://localhost:8000/api/favorites/${id}`, { method: "DELETE" }).then(() => fetchStocks());
    }
  };

  return (
    <div style={{ maxWidth: '500px', margin: '0 auto', backgroundColor: '#f5f5f5', minHeight: '100vh', display: 'flex', flexDirection: 'column', fontFamily: "'맑은 고딕', sans-serif" }}>
      <div style={{ backgroundColor: '#1a73e8', color: 'white', padding: '20px', textAlign: 'center', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        <h1 style={{ margin: 0, fontSize: '1.5rem' }}>AI 뉴스 큐레이터</h1>
        <p style={{ margin: '5px 0 0', fontSize: '0.8rem', opacity: 0.9 }}>실시간 주요 뉴스 브리핑</p>
      </div>

      {currentMenu === 'home' && (
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', overflowX: 'auto', padding: '10px', gap: '10px', backgroundColor: 'white', whiteSpace: 'nowrap', borderBottom: '1px solid #ddd' }}>
            {ALL_CATEGORIES.filter(cat => enabledCategories.includes(cat.id)).map(cat => (
              <button key={cat.id} onClick={() => setActiveTab(cat.id)} style={{ padding: '8px 16px', borderRadius: '20px', border: 'none', backgroundColor: activeTab === cat.id ? '#1a73e8' : '#f1f3f4', color: activeTab === cat.id ? 'white' : '#5f6368', fontWeight: 'bold', cursor: 'pointer', transition: 'all 0.2s' }}>{cat.name}</button>
            ))}
          </div>
          <div style={{ flex: 1, padding: '15px' }}>
            {isLoading ? <div style={{ textAlign: 'center', padding: '50px', color: '#888' }}>로딩 중...</div> : (
              newsList.map((news) => (
                <div key={news.id} onClick={() => openNewsLink(news.url)} style={{ backgroundColor: 'white', padding: '15px', borderRadius: '12px', marginBottom: '15px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', cursor: 'pointer' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}><span style={{ fontSize: '0.75rem', color: '#1a73e8', fontWeight: 'bold' }}>{ALL_CATEGORIES.find(c => c.id === news.category_code)?.name}</span><span style={{ fontSize: '0.75rem', color: '#999' }}>{news.created_at}</span></div>
                  <h3 style={{ margin: '0 0 10px 0', fontSize: '1.05rem', color: '#202124' }}>{news.title}</h3>
                  <p style={{ margin: 0, fontSize: '0.9rem', color: '#5f6368', display: '-webkit-box', WebkitLineClamp: '2', WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>{news.ai_summary}</p>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {currentMenu === 'calendar' && <div style={{ flex: 1 }}><Calendar /></div>}
      {currentMenu === 'clipboard' && <div style={{ flex: 1, overflowY: 'auto' }}><Clipboard /></div>}

      {currentMenu === 'settings' && (
        <div style={{ flex: 1, padding: '20px', overflowY: 'auto' }}>
           <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '15px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)', marginBottom: '20px' }}>
             <h2 style={{ margin: '0 0 20px 0', fontSize: '1.2rem', color: '#1a73e8' }}>⚙️ 시스템 설정</h2>
             <p style={{ fontWeight: 'bold', marginBottom: '10px' }}>🔔 알람 브리핑 주기</p>
             <select value={alarmInterval} onChange={(e) => handleIntervalChange(e.target.value)} style={{ padding: '10px', width: '100%', borderRadius: '8px', border: '1px solid #ddd', fontSize: '1rem', marginBottom: '25px' }}>
               <option value={1}>1분마다 (테스트)</option><option value={5}>5분마다</option><option value={10}>10분마다 (기본)</option><option value={30}>30분마다</option><option value={60}>1시간마다</option>
             </select>
             <p style={{ fontWeight: 'bold', marginBottom: '10px' }}>📰 관심 분야 선택</p>
             <div style={{ display: 'flex', overflowX: 'auto', gap: '12px', marginBottom: '25px', paddingBottom: '10px', whiteSpace: 'nowrap' }}>
                {ALL_CATEGORIES.map(cat => (
                  <label key={cat.id} style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 15px', backgroundColor: '#f8f9fa', borderRadius: '8px', cursor: 'pointer', flexShrink: 0 }}>
                    <input type="checkbox" checked={enabledCategories.includes(cat.id)} onChange={() => handleCategoryToggle(cat.id)} style={{ width: '18px', height: '18px' }}/><span style={{ fontSize: '0.9rem' }}>{cat.name}</span>
                  </label>
                ))}
             </div>
             <div style={{ borderTop: '1px solid #eee', paddingTop: '20px' }}>
               <p style={{ fontWeight: 'bold', marginBottom: '10px' }}>⏱️ 말풍선 유지 시간 (초)</p><input type="number" value={bubbleDuration} onChange={(e) => handleDurationChange(e.target.value)} style={{ padding: '10px', width: '100%', borderRadius: '8px', border: '1px solid #ddd', marginBottom: '20px' }} />
               <p style={{ fontWeight: 'bold', marginBottom: '10px' }}>🔢 브리핑 뉴스 개수 (0은 무한)</p><input type="number" value={newsCount} onChange={(e) => handleCountChange(e.target.value)} style={{ padding: '10px', width: '100%', borderRadius: '8px', border: '1px solid #ddd' }} />
             </div>
           </div>

           <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '15px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' }}>
             <h2 style={{ margin: '0 0 20px 0', fontSize: '1.2rem', color: '#34a853' }}>📈 관심 주식 종목 관리</h2>
             
             <div style={{ marginBottom: '15px' }}>
               <div style={{ display: 'flex', gap: '8px' }}>
                  <input type="text" placeholder="종목명 입력 (예: 삼성전자, 애플)" value={newStockName} onChange={e => handleSearchChange(e.target.value)} onKeyDown={e => e.key === 'Enter' && handleAddStock()} style={{ flex: 1, padding: '10px', borderRadius: '6px', border: '1px solid #ddd' }} />
                  <button id="addStockBtn" onClick={() => handleAddStock(newStockName)} style={{ padding: '0 15px', backgroundColor: '#34a853', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>추가</button>
               </div>
               
               {searchResults.length > 0 && (
                 <ul style={{ backgroundColor: 'white', border: '1px solid #ddd', borderRadius: '6px', marginTop: '4px', padding: 0, listStyle: 'none', maxHeight: '150px', overflowY: 'auto', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
                   {searchResults.map((stock, idx) => (
                     <li 
                       key={idx} 
                       onClick={() => handleSelectAndAdd(stock.name, stock.ticker)} // 💡 이제 클릭 시 티커(코드)를 챙겨서 보냅니다!
                       style={{ padding: '10px 15px', borderBottom: '1px solid #eee', cursor: 'pointer', fontSize: '0.9rem', color: '#333' }}
                     >
                       <span style={{ fontWeight: 'bold', color: '#1a73e8' }}>{stock.name}</span> <span style={{ fontSize: '0.8rem', color: '#888' }}>({stock.ticker})</span>
                     </li>
                   ))}
                 </ul>
               )}
             </div>

             <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
               {favoriteStocks.map(stock => (
                 <li key={stock.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '10px', borderBottom: '1px solid #eee' }}><span><strong>{stock.name}</strong> <span style={{color:'#888', fontSize:'0.85rem'}}>({stock.ticker})</span></span><button onClick={() => handleDeleteStock(stock.id)} style={{ color: '#ea4335', background: 'none', border: 'none', cursor: 'pointer' }}>✖ 삭제</button></li>
               ))}
               {favoriteStocks.length === 0 && <li style={{ textAlign: 'center', color: '#999', padding: '10px' }}>등록된 종목이 없습니다.</li>}
             </ul>
           </div>
        </div>
      )}

      <div style={{ display: 'flex', borderTop: '1px solid #ddd', backgroundColor: 'white', position: 'sticky', bottom: 0, padding: '5px 0' }}>
        <div onClick={() => setCurrentMenu('home')} style={{ flex: 1, textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px', color: currentMenu === 'home' ? '#1a73e8' : '#9aa0a6', cursor: 'pointer' }}><span style={{ fontSize: '20px' }}>🏠</span><span style={{ fontSize: '11px', fontWeight: currentMenu === 'home' ? 'bold' : 'normal' }}>홈</span></div>
        <div onClick={() => setCurrentMenu('calendar')} style={{ flex: 1, textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px', color: currentMenu === 'calendar' ? '#1a73e8' : '#9aa0a6', cursor: 'pointer' }}><span style={{ fontSize: '20px' }}>📅</span><span style={{ fontSize: '11px', fontWeight: currentMenu === 'calendar' ? 'bold' : 'normal' }}>달력</span></div>
        <div onClick={() => setCurrentMenu('clipboard')} style={{ flex: 1, textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px', color: currentMenu === 'clipboard' ? '#1a73e8' : '#9aa0a6', cursor: 'pointer' }}><span style={{ fontSize: '20px' }}>📋</span><span style={{ fontSize: '11px', fontWeight: currentMenu === 'clipboard' ? 'bold' : 'normal' }}>클립보드</span></div>
        <div onClick={() => setCurrentMenu('settings')} style={{ flex: 1, textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px', color: currentMenu === 'settings' ? '#1a73e8' : '#9aa0a6', cursor: 'pointer' }}><span style={{ fontSize: '20px' }}>⚙️</span><span style={{ fontSize: '11px', fontWeight: currentMenu === 'settings' ? 'bold' : 'normal' }}>설정</span></div>
      </div>
    </div>
  )
}