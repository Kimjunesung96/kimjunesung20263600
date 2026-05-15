import { useState, useEffect, useRef } from 'react'
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

  // 주식 관심종목 상태
  const [favoriteStocks, setFavoriteStocks] = useState([]);
  const [newStockName, setNewStockName] = useState("");

  // 💡 추천 검색어 상태
  const [stockSuggestions, setStockSuggestions] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const searchTimerRef = useRef(null);

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
      body: JSON.stringify({ 
        alarm_interval: newInterval, enabled_categories: newCategories,
        bubble_duration: parseInt(newDuration) || 0, news_count: parseInt(newCount) || 0
      })
    });
  };

  const handleIntervalChange = (val) => {
    setAlarmInterval(parseInt(val)); saveAllSettings(parseInt(val), enabledCategories, bubbleDuration, newsCount);
  };

  const handleCategoryToggle = (id) => {
    const next = enabledCategories.includes(id) ? enabledCategories.filter(c => c !== id) : [...enabledCategories, id];
    if (next.length === 0) return;
    setEnabledCategories(next); saveAllSettings(alarmInterval, next, bubbleDuration, newsCount);
  };

  const handleDurationChange = (val) => {
    setBubbleDuration(val); saveAllSettings(alarmInterval, enabledCategories, val, newsCount);
  };

  const handleCountChange = (val) => {
    setNewsCount(val); saveAllSettings(alarmInterval, enabledCategories, bubbleDuration, val);
  };

  // 💡 입력할 때마다 0.4초 뒤에 추천 검색어 요청 (디바운싱)
  const handleStockInput = (val) => {
    setNewStockName(val);
    setStockSuggestions([]);

    if (searchTimerRef.current) clearTimeout(searchTimerRef.current);
    if (val.trim().length < 1) return;

    searchTimerRef.current = setTimeout(() => {
      setIsSearching(true);
      fetch(`http://localhost:8000/api/search_stock?name=${encodeURIComponent(val.trim())}`)
        .then(res => res.json())
        .then(data => {
          if (data.status === 'success') setStockSuggestions(data.data);
        })
        .catch(() => {})
        .finally(() => setIsSearching(false));
    }, 400);
  };

  // 💡 추천 종목 클릭 시 바로 등록
  const selectSuggestion = (item) => {
    fetch("http://localhost:8000/api/favorites", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: item.name })
    })
    .then(res => res.json())
    .then(data => {
      if (data.status === 'success') {
        fetchStocks();
        setNewStockName("");
        setStockSuggestions([]);
      } else {
        alert("❌ " + data.message);
      }
    });
  };

  // 💡 직접 추가 버튼
  const handleAddStock = () => {
    if (!newStockName.trim()) return alert("종목명을 입력해주세요!");
    setStockSuggestions([]);

    fetch("http://localhost:8000/api/favorites", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: newStockName.trim() }) 
    })
    .then(res => res.json())
    .then(data => {
      if(data.status === 'success') { 
        fetchStocks(); 
        setNewStockName(""); 
      }
      else alert("❌ " + data.message);
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

      {/* 홈 화면 (뉴스) */}
      {currentMenu === 'home' && (
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', overflowX: 'auto', padding: '10px', gap: '10px', backgroundColor: 'white', whiteSpace: 'nowrap', borderBottom: '1px solid #ddd' }}>
            {ALL_CATEGORIES.filter(cat => enabledCategories.includes(cat.id)).map(cat => (
              <button key={cat.id} onClick={() => setActiveTab(cat.id)} style={{ padding: '8px 16px', borderRadius: '20px', border: 'none', backgroundColor: activeTab === cat.id ? '#1a73e8' : '#f1f3f4', color: activeTab === cat.id ? 'white' : '#5f6368', fontWeight: 'bold', cursor: 'pointer', transition: 'all 0.2s' }}>
                {cat.name}
              </button>
            ))}
          </div>
          <div style={{ flex: 1, padding: '15px' }}>
            {isLoading ? <div style={{ textAlign: 'center', padding: '50px', color: '#888' }}>로딩 중...</div> : (
              newsList.map((news) => (
                <div key={news.id} onClick={() => openNewsLink(news.url)} style={{ backgroundColor: 'white', padding: '15px', borderRadius: '12px', marginBottom: '15px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', cursor: 'pointer' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span style={{ fontSize: '0.75rem', color: '#1a73e8', fontWeight: 'bold' }}>{ALL_CATEGORIES.find(c => c.id === news.category_code)?.name}</span>
                    <span style={{ fontSize: '0.75rem', color: '#999' }}>{news.created_at}</span>
                  </div>
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

      {/* 설정 화면 */}
      {currentMenu === 'settings' && (
        <div style={{ flex: 1, padding: '20px', overflowY: 'auto' }}>
           <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '15px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)', marginBottom: '20px' }}>
             <h2 style={{ margin: '0 0 20px 0', fontSize: '1.2rem', color: '#1a73e8' }}>⚙️ 시스템 설정</h2>
             
             <p style={{ fontWeight: 'bold', marginBottom: '10px' }}>🔔 알람 브리핑 주기</p>
             <select value={alarmInterval} onChange={(e) => handleIntervalChange(e.target.value)} style={{ padding: '10px', width: '100%', borderRadius: '8px', border: '1px solid #ddd', fontSize: '1rem', marginBottom: '25px' }}>
               <option value={1}>1분마다 (테스트)</option><option value={5}>5분마다</option><option value={10}>10분마다 (기본)</option><option value={30}>30분마다</option><option value={60}>1시간마다</option>
             </select>

             <p style={{ fontWeight: 'bold', marginBottom: '10px' }}>📰 관심 분야 선택 (홈 화면 표시)</p>
             <div style={{ display: 'flex', overflowX: 'auto', gap: '12px', marginBottom: '25px', paddingBottom: '10px', whiteSpace: 'nowrap' }}>
                {ALL_CATEGORIES.map(cat => (
                  <label key={cat.id} style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 15px', backgroundColor: '#f8f9fa', borderRadius: '8px', cursor: 'pointer', flexShrink: 0 }}>
                    <input type="checkbox" checked={enabledCategories.includes(cat.id)} onChange={() => handleCategoryToggle(cat.id)} style={{ width: '18px', height: '18px' }}/>
                    <span style={{ fontSize: '0.9rem' }}>{cat.name}</span>
                  </label>
                ))}
             </div>

             <div style={{ borderTop: '1px solid #eee', paddingTop: '20px' }}>
               <p style={{ fontWeight: 'bold', marginBottom: '10px' }}>⏱️ 말풍선 유지 시간 (초)</p>
               <input type="number" value={bubbleDuration} onChange={(e) => handleDurationChange(e.target.value)} style={{ padding: '10px', width: '100%', borderRadius: '8px', border: '1px solid #ddd', marginBottom: '20px' }} />

               <p style={{ fontWeight: 'bold', marginBottom: '10px' }}>🔢 브리핑 뉴스 개수 (0은 무한)</p>
               <input type="number" value={newsCount} onChange={(e) => handleCountChange(e.target.value)} style={{ padding: '10px', width: '100%', borderRadius: '8px', border: '1px solid #ddd' }} />
             </div>
           </div>

           {/* 💡 관심 주식 종목 관리 패널 */}
           <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '15px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' }}>
             <h2 style={{ margin: '0 0 20px 0', fontSize: '1.2rem', color: '#34a853' }}>📈 관심 주식 종목 관리</h2>
             
             {/* 💡 입력창 + 추천 드롭다운 */}
             <div style={{ position: 'relative', marginBottom: '15px' }}>
               <div style={{ display: 'flex', gap: '8px' }}>
                 <input
                   type="text"
                   placeholder="종목명 입력 (예: 삼성전자, 아마존)"
                   value={newStockName}
                   onChange={e => handleStockInput(e.target.value)}
                   onKeyDown={e => e.key === 'Enter' && handleAddStock()}
                   style={{ flex: 1, padding: '10px', borderRadius: '6px', border: '1px solid #ddd', fontSize: '0.95rem' }}
                 />
                 <button
                   id="addStockBtn"
                   onClick={handleAddStock}
                   style={{ padding: '0 16px', backgroundColor: '#34a853', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold', whiteSpace: 'nowrap' }}
                 >
                   {isSearching ? "검색중..." : "추가"}
                 </button>
               </div>

               {/* 💡 추천 드롭다운 */}
               {stockSuggestions.length > 0 && (
                 <div style={{ position: 'absolute', top: '100%', left: 0, right: '80px', backgroundColor: 'white', border: '1px solid #ddd', borderRadius: '8px', boxShadow: '0 4px 12px rgba(0,0,0,0.15)', zIndex: 100, marginTop: '4px', overflow: 'hidden' }}>
                   {stockSuggestions.map((item, idx) => (
                     <div
                       key={idx}
                       onClick={() => selectSuggestion(item)}
                       style={{ padding: '10px 14px', cursor: 'pointer', borderBottom: idx < stockSuggestions.length - 1 ? '1px solid #f1f1f1' : 'none', display: 'flex', justifyContent: 'space-between', alignItems: 'center', backgroundColor: 'white', transition: 'background 0.15s' }}
                       onMouseEnter={e => e.currentTarget.style.backgroundColor = '#f0f4ff'}
                       onMouseLeave={e => e.currentTarget.style.backgroundColor = 'white'}
                     >
                       <span style={{ fontWeight: 'bold', color: '#202124', fontSize: '0.9rem' }}>{item.name}</span>
                       <span style={{ fontSize: '0.75rem', color: '#888', backgroundColor: '#f1f3f4', padding: '2px 8px', borderRadius: '10px' }}>{item.ticker}</span>
                     </div>
                   ))}
                 </div>
               )}
             </div>

             <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
               {favoriteStocks.map(stock => (
                 <li key={stock.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '10px', borderBottom: '1px solid #eee' }}>
                   <span><strong>{stock.name}</strong> <span style={{color:'#888', fontSize:'0.85rem'}}>({stock.ticker})</span></span>
                   <button onClick={() => handleDeleteStock(stock.id)} style={{ color: '#ea4335', background: 'none', border: 'none', cursor: 'pointer' }}>✖ 삭제</button>
                 </li>
               ))}
               {favoriteStocks.length === 0 && <li style={{ textAlign: 'center', color: '#999', padding: '10px' }}>등록된 종목이 없습니다.</li>}
             </ul>
             <p style={{ fontSize: '0.8rem', color: '#888', marginTop: '15px' }}>* 입력하신 한국/미국 주식 이름으로 시스템이 티커를 자동 검색합니다.</p>
           </div>
        </div>
      )}

      {/* 하단 네비게이션바 */}
      <div style={{ display: 'flex', borderTop: '1px solid #ddd', backgroundColor: 'white', position: 'sticky', bottom: 0, padding: '5px 0' }}>
        <div onClick={() => setCurrentMenu('home')} style={{ flex: 1, textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px', color: currentMenu === 'home' ? '#1a73e8' : '#9aa0a6', cursor: 'pointer' }}><span style={{ fontSize: '20px' }}>🏠</span><span style={{ fontSize: '11px', fontWeight: currentMenu === 'home' ? 'bold' : 'normal' }}>홈</span></div>
        <div onClick={() => setCurrentMenu('calendar')} style={{ flex: 1, textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px', color: currentMenu === 'calendar' ? '#1a73e8' : '#9aa0a6', cursor: 'pointer' }}><span style={{ fontSize: '20px' }}>📅</span><span style={{ fontSize: '11px', fontWeight: currentMenu === 'calendar' ? 'bold' : 'normal' }}>달력</span></div>
        <div onClick={() => setCurrentMenu('clipboard')} style={{ flex: 1, textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px', color: currentMenu === 'clipboard' ? '#1a73e8' : '#9aa0a6', cursor: 'pointer' }}><span style={{ fontSize: '20px' }}>📋</span><span style={{ fontSize: '11px', fontWeight: currentMenu === 'clipboard' ? 'bold' : 'normal' }}>클립보드</span></div>
        <div onClick={() => setCurrentMenu('settings')} style={{ flex: 1, textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px', color: currentMenu === 'settings' ? '#1a73e8' : '#9aa0a6', cursor: 'pointer' }}><span style={{ fontSize: '20px' }}>⚙️</span><span style={{ fontSize: '11px', fontWeight: currentMenu === 'settings' ? 'bold' : 'normal' }}>설정</span></div>
      </div>
    </div>
  )
}