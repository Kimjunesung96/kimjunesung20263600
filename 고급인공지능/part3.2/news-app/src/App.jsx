import { useState, useEffect, useRef } from 'react';
import Calendar from './Calendar';
import Clipboard from './Clipboard';
import NewsTab from './components/NewsTab';
import StockTab from './components/StockTab';
import SettingsTab from './components/SettingsTab';

export default function App() {
  const [currentMenu, setCurrentMenu] = useState('home');
  const [homeMode, setHomeMode] = useState('news');

  // 뉴스 탭 상태
  const [activeTab, setActiveTab] = useState('01');
  const [searchKeyword, setSearchKeyword] = useState('');

  // 설정 상태
  const [alarmInterval, setAlarmInterval] = useState(10);
  const [enabledCategories, setEnabledCategories] = useState(['01', '02', '03']);
  const [bubbleDuration, setBubbleDuration] = useState(5);
  const [newsCount, setNewsCount] = useState(10);

  // 주식 상태
  const [favoriteStocks, setFavoriteStocks] = useState([]);

  const alarmIntervalRef = useRef(alarmInterval);
  useEffect(() => { alarmIntervalRef.current = alarmInterval; }, [alarmInterval]);

  // 초기 설정 + 주식 목록 로드
  useEffect(() => {
    fetch('http://localhost:8000/api/settings')
      .then(res => res.json())
      .then(data => {
        if (data.alarm_interval)       setAlarmInterval(data.alarm_interval);
        if (data.enabled_categories)   setEnabledCategories(data.enabled_categories);
        if (data.bubble_duration != null) setBubbleDuration(data.bubble_duration);
        if (data.news_count      != null) setNewsCount(data.news_count);
      });
    fetchStocks();
  }, []);

  // URL 쿼리 파라미터로 검색어 처리
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const query = params.get('search');
    if (query) {
      setSearchKeyword(query);
      setActiveTab('search');
      setHomeMode('news');
    }
  }, []);

  const fetchStocks = () => {
    fetch('http://localhost:8000/api/favorites')
      .then(res => res.json())
      .then(data => {
        if (data.status === 'success') setFavoriteStocks(data.data);
      });
  };

  // 설정 저장
  const saveAllSettings = (interval, categories, duration, count) => {
    fetch('http://localhost:8000/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        alarm_interval: interval,
        enabled_categories: categories,
        bubble_duration: parseInt(duration) || 0,
        news_count: parseInt(count) || 0,
      }),
    });
  };

  const handleIntervalChange = (val) => {
    const parsed = parseInt(val);
    setAlarmInterval(parsed);
    alarmIntervalRef.current = parsed;
    saveAllSettings(parsed, enabledCategories, bubbleDuration, newsCount);
  };
  const handleCategoryToggle = (id) => {
    const next = enabledCategories.includes(id)
      ? enabledCategories.filter(c => c !== id)
      : [...enabledCategories, id];
    if (next.length === 0) return;
    setEnabledCategories(next);
    saveAllSettings(alarmInterval, next, bubbleDuration, newsCount);
  };
  const handleDurationChange = (val) => {
    setBubbleDuration(val);
    saveAllSettings(alarmInterval, enabledCategories, val, newsCount);
  };
  const handleCountChange = (val) => {
    setNewsCount(val);
    saveAllSettings(alarmInterval, enabledCategories, bubbleDuration, val);
  };

  // 주식 종목 삭제 시 activeStock 초기화는 StockTab 내부에서 처리
  const handleStocksChange = () => fetchStocks();

  return (
    <div style={{ maxWidth: '500px', margin: '0 auto', backgroundColor: '#f5f5f5', height: '100vh', overflow: 'hidden', display: 'flex', flexDirection: 'column', fontFamily: "'맑은 고딕', sans-serif" }}>

      {/* 헤더 */}
      <div style={{ backgroundColor: '#1a73e8', color: 'white', paddingTop: '15px', textAlign: 'center', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        <h1 style={{ margin: 0, fontSize: '1.5rem', marginBottom: '4px' }}>AI 뉴스 큐레이터</h1>
        <p style={{ margin: '0 0 0 0', fontSize: '0.8rem', opacity: 0.8 }}>실시간 주요 뉴스 브리핑</p>

        {currentMenu === 'home' && (
          <div style={{ display: 'flex', padding: '0 15px', marginTop: '10px' }}>
            <div onClick={() => setHomeMode('news')}
              style={{ flex: 1, padding: '10px 0', fontWeight: 'bold', cursor: 'pointer', borderBottom: homeMode === 'news' ? '3px solid white' : '3px solid transparent', color: homeMode === 'news' ? 'white' : 'rgba(255,255,255,0.6)', transition: 'all 0.2s' }}>
              📰 주요 뉴스
            </div>
            <div onClick={() => { setHomeMode('stock'); setSearchKeyword(''); }}
              style={{ flex: 1, padding: '10px 0', fontWeight: 'bold', cursor: 'pointer', borderBottom: homeMode === 'stock' ? '3px solid white' : '3px solid transparent', color: homeMode === 'stock' ? 'white' : 'rgba(255,255,255,0.6)', transition: 'all 0.2s' }}>
              📈 관심 주식
            </div>
          </div>
        )}
      </div>

      {/* 홈 - 뉴스 / 주식 */}
      {currentMenu === 'home' && homeMode === 'news' && (
        <NewsTab
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          searchKeyword={searchKeyword}
          setSearchKeyword={setSearchKeyword}
          enabledCategories={enabledCategories}
          alarmInterval={alarmInterval}
          currentMenu={currentMenu}
        />
      )}
      {currentMenu === 'home' && homeMode === 'stock' && (
        <StockTab
          favoriteStocks={favoriteStocks}
          currentMenu={currentMenu}
        />
      )}

      {/* 달력 / 클립보드 */}
      {currentMenu === 'calendar'  && <div style={{ flex: 1 }}><Calendar /></div>}
      {currentMenu === 'clipboard' && <div style={{ flex: 1, overflowY: 'auto' }}><Clipboard /></div>}

      {/* 설정 */}
      {currentMenu === 'settings' && (
        <SettingsTab
          alarmInterval={alarmInterval}     onIntervalChange={handleIntervalChange}
          enabledCategories={enabledCategories} onCategoryToggle={handleCategoryToggle}
          bubbleDuration={bubbleDuration}   onDurationChange={handleDurationChange}
          newsCount={newsCount}             onCountChange={handleCountChange}
          favoriteStocks={favoriteStocks}   onStocksChange={handleStocksChange}
        />
      )}

      {/* 하단 네비게이션 */}
      <div style={{ display: 'flex', borderTop: '1px solid #ddd', backgroundColor: 'white', position: 'sticky', bottom: 0, padding: '5px 0', flexShrink: 0 }}>
        {[
          { key: 'home',      icon: '🏠', label: '홈' },
          { key: 'calendar',  icon: '📅', label: '달력' },
          { key: 'clipboard', icon: '📋', label: '클립보드' },
          { key: 'settings',  icon: '⚙️', label: '설정' },
        ].map(({ key, icon, label }) => (
          <div key={key} onClick={() => setCurrentMenu(key)}
            style={{ flex: 1, textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px', color: currentMenu === key ? '#1a73e8' : '#9aa0a6', cursor: 'pointer' }}>
            <span style={{ fontSize: '20px' }}>{icon}</span>
            <span style={{ fontSize: '11px', fontWeight: currentMenu === key ? 'bold' : 'normal' }}>{label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}