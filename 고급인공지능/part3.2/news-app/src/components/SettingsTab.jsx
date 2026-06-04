import { useState } from 'react';

const ALL_CATEGORIES = [
  { id: '01', name: 'IT/테크' }, { id: '02', name: '경제' },
  { id: '03', name: '사회' },   { id: '04', name: '세계' },
  { id: '05', name: '연예' },   { id: '06', name: '스포츠' },
  { id: '07', name: '과학' },   { id: '08', name: '건강' },
];

export default function SettingsTab({
  alarmInterval, onIntervalChange,
  enabledCategories, onCategoryToggle,
  bubbleDuration, onDurationChange,
  newsCount, onCountChange,
  favoriteStocks, onStocksChange,
}) {
  const [newStockName, setNewStockName] = useState('');
  const [searchResults, setSearchResults] = useState([]);

  const handleSearchChange = (val) => {
    setNewStockName(val);
    if (!val.trim()) { setSearchResults([]); return; }
    fetch(`http://localhost:8000/api/search_stock?name=${encodeURIComponent(val)}`)
      .then(res => res.json())
      .then(data => { if (data.status === 'success') setSearchResults(data.data); })
      .catch(() => setSearchResults([]));
  };

  const handleSelectAndAdd = (stockName, stockTicker) => {
    setNewStockName('');
    setSearchResults([]);
    handleAddStock(stockName, stockTicker);
  };

  const handleAddStock = (targetName = newStockName, targetTicker = '') => {
    if (!targetName.trim()) return alert('종목명을 입력해주세요!');
    const btn = document.getElementById('addStockBtn');
    if (btn) { btn.innerText = '추가 중...'; btn.disabled = true; }
    fetch('http://localhost:8000/api/favorites', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: targetName.trim(), ticker: targetTicker }),
    })
      .then(res => res.json())
      .then(data => {
        if (data.status === 'success') {
          setNewStockName('');
          setSearchResults([]);
          onStocksChange();
        } else {
          alert('❌ ' + data.message);
        }
      })
      .finally(() => { if (btn) { btn.innerText = '추가'; btn.disabled = false; } });
  };

  const handleDeleteStock = (id) => {
    if (window.confirm('이 종목을 삭제할까요?')) {
      fetch(`http://localhost:8000/api/favorites/${id}`, { method: 'DELETE' })
        .then(() => onStocksChange(id));
    }
  };

  return (
    <div style={{ flex: 1, padding: '20px', overflowY: 'auto' }}>

      {/* 시스템 설정 */}
      <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '15px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)', marginBottom: '20px' }}>
        <h2 style={{ margin: '0 0 20px 0', fontSize: '1.2rem', color: '#1a73e8' }}>⚙️ 시스템 설정</h2>

        <p style={{ fontWeight: 'bold', marginBottom: '10px' }}>🔔 알람 브리핑 주기</p>
        <select value={alarmInterval} onChange={(e) => onIntervalChange(e.target.value)}
          style={{ padding: '10px', width: '100%', borderRadius: '8px', border: '1px solid #ddd', fontSize: '1rem', marginBottom: '25px' }}>
          <option value={1}>1분마다 (테스트)</option>
          <option value={5}>5분마다</option>
          <option value={10}>10분마다 (기본)</option>
          <option value={30}>30분마다</option>
          <option value={60}>1시간마다</option>
        </select>

        <p style={{ fontWeight: 'bold', marginBottom: '10px' }}>📰 관심 분야 선택</p>
        <div style={{ display: 'flex', overflowX: 'auto', gap: '12px', marginBottom: '25px', paddingBottom: '10px', whiteSpace: 'nowrap' }}>
          {ALL_CATEGORIES.map(cat => (
            <label key={cat.id} style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 15px', backgroundColor: '#f8f9fa', borderRadius: '8px', cursor: 'pointer', flexShrink: 0 }}>
              <input type="checkbox" checked={enabledCategories.includes(cat.id)} onChange={() => onCategoryToggle(cat.id)}
                style={{ width: '18px', height: '18px' }} />
              <span style={{ fontSize: '0.9rem' }}>{cat.name}</span>
            </label>
          ))}
        </div>

        <div style={{ borderTop: '1px solid #eee', paddingTop: '20px' }}>
          <p style={{ fontWeight: 'bold', marginBottom: '10px' }}>⏱️ 말풍선 유지 시간 (초)</p>
          <input type="number" value={bubbleDuration} onChange={(e) => onDurationChange(e.target.value)}
            style={{ padding: '10px', width: '100%', borderRadius: '8px', border: '1px solid #ddd', marginBottom: '20px' }} />

          <p style={{ fontWeight: 'bold', marginBottom: '10px' }}>🔢 브리핑 뉴스 개수 (0은 무한)</p>
          <input type="number" value={newsCount} onChange={(e) => onCountChange(e.target.value)}
            style={{ padding: '10px', width: '100%', borderRadius: '8px', border: '1px solid #ddd' }} />
        </div>
      </div>

      {/* 관심 주식 관리 */}
      <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '15px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' }}>
        <h2 style={{ margin: '0 0 20px 0', fontSize: '1.2rem', color: '#34a853' }}>📈 관심 주식 종목 관리</h2>

        <div style={{ marginBottom: '15px' }}>
          <div style={{ display: 'flex', gap: '8px' }}>
            <input type="text" placeholder="종목명 입력 (예: 삼성전자, 애플)"
              value={newStockName} onChange={e => handleSearchChange(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleAddStock()}
              style={{ flex: 1, padding: '10px', borderRadius: '6px', border: '1px solid #ddd' }} />
            <button id="addStockBtn" onClick={() => handleAddStock(newStockName)}
              style={{ padding: '0 15px', backgroundColor: '#34a853', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>
              추가
            </button>
          </div>

          {searchResults.length > 0 && (
            <ul style={{ backgroundColor: 'white', border: '1px solid #ddd', borderRadius: '6px', marginTop: '4px', padding: 0, listStyle: 'none', maxHeight: '150px', overflowY: 'auto', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
              {searchResults.map((stock, idx) => (
                <li key={idx} onClick={() => handleSelectAndAdd(stock.name, stock.ticker)}
                  style={{ padding: '10px 15px', borderBottom: '1px solid #eee', cursor: 'pointer', fontSize: '0.9rem', color: '#333' }}>
                  <span style={{ fontWeight: 'bold', color: '#1a73e8' }}>{stock.name}</span>{' '}
                  <span style={{ fontSize: '0.8rem', color: '#888' }}>({stock.ticker})</span>
                </li>
              ))}
            </ul>
          )}
        </div>

        <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
          {favoriteStocks.map(stock => (
            <li key={stock.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px', borderBottom: '1px solid #eee' }}>
              <span>
                <strong>{stock.name}</strong>{' '}
                <span style={{ color: '#888', fontSize: '0.85rem' }}>({stock.ticker})</span>
              </span>
              <button onClick={() => handleDeleteStock(stock.id)}
                style={{ color: '#ea4335', background: 'none', border: 'none', cursor: 'pointer', fontSize: '0.9rem' }}>
                ✖ 삭제
              </button>
            </li>
          ))}
          {favoriteStocks.length === 0 && (
            <li style={{ textAlign: 'center', color: '#999', padding: '15px' }}>등록된 종목이 없습니다.</li>
          )}
        </ul>
      </div>
    </div>
  );
}