import { useState, useEffect, useCallback, useRef } from 'react';

const ALL_CATEGORIES = [
  { id: '01', name: 'IT/테크' }, { id: '02', name: '경제' },
  { id: '03', name: '사회' },   { id: '04', name: '세계' },
  { id: '05', name: '연예' },   { id: '06', name: '스포츠' },
  { id: '07', name: '과학' },   { id: '08', name: '건강' },
];

export default function StockTab({ favoriteStocks, currentMenu }) {
  const [activeStock, setActiveStock] = useState(null);
  const [stockDetail, setStockDetail] = useState(null);
  const [newsList, setNewsList] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);

  // 첫 번째 종목 자동 선택
  useEffect(() => {
    if (!activeStock && favoriteStocks.length > 0) {
      setActiveStock(favoriteStocks[0]);
    }
  }, [favoriteStocks]);

  const fetchStockData = useCallback((isBackground = false) => {
    if (!activeStock?.ticker) return;
    if (!isBackground) {
      setIsLoading(true);
      setStockDetail(null);
      setNewsList([]);
    }

    fetch(`http://localhost:8000/api/stock/${activeStock.ticker}`)
      .then(res => res.json())
      .then(data => {
        if (data.status === 'success') setStockDetail(data);
        else if (!isBackground) setStockDetail(null);
      })
      .catch(() => { if (!isBackground) setStockDetail(null); });

    fetch(`http://localhost:8000/api/search?q=${encodeURIComponent(activeStock.name)}&limit=30&offset=0`)
      .then(res => res.json())
      .then(result => {
        if (result.status === 'success') {
          setNewsList(result.data);
          setLastUpdated(new Date());
        }
        if (!isBackground) setIsLoading(false);
      })
      .catch(() => { if (!isBackground) setIsLoading(false); });
  }, [activeStock]);

  // 종목 바뀌거나 탭 돌아올 때 갱신
  useEffect(() => {
    if (currentMenu !== 'home' || !activeStock?.ticker) return;
    fetchStockData(false);
    const intervalId = setInterval(() => fetchStockData(true), 30 * 1000);
    return () => clearInterval(intervalId);
  }, [activeStock, currentMenu, fetchStockData]);

  const formatLastUpdated = (date) => {
    if (!date) return null;
    return date.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  };

  const openNewsLink = (url) => window.open(url, '_blank');

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>

      {/* 종목 버튼 바 */}
      <div style={{ display: 'flex', overflowX: 'auto', padding: '10px', gap: '8px', backgroundColor: 'white', whiteSpace: 'nowrap', borderBottom: '1px solid #ddd', flexShrink: 0 }}>
        {favoriteStocks.length > 0
          ? favoriteStocks.map(stock => (
              <button key={stock.id} onClick={() => setActiveStock(stock)}
                style={{ padding: '8px 16px', borderRadius: '20px', border: 'none', backgroundColor: activeStock?.id === stock.id ? '#34a853' : '#e6f4ea', color: activeStock?.id === stock.id ? 'white' : '#137333', fontWeight: 'bold', cursor: 'pointer', transition: 'all 0.2s', flexShrink: 0 }}>
                {stock.name}
              </button>
            ))
          : <span style={{ color: '#888', fontSize: '0.85rem', padding: '8px 5px' }}>⚙️ 설정에서 관심 종목을 먼저 등록해주세요.</span>
        }
      </div>

      {/* 스크롤 컨테이너 */}
      <div style={{ flex: 1, padding: '15px', overflowY: 'auto' }}>

        {/* 갱신 시간 + 새로고침 */}
        {activeStock && (
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
            <span style={{ fontSize: '0.75rem', color: '#aaa' }}>
              {lastUpdated ? `🕐 ${formatLastUpdated(lastUpdated)} 갱신` : ''}
            </span>
            <button onClick={() => fetchStockData(false)}
              style={{ fontSize: '0.75rem', padding: '4px 10px', backgroundColor: '#f1f3f4', border: '1px solid #ddd', borderRadius: '12px', cursor: 'pointer', color: '#5f6368' }}>
              🔄 새로고침
            </button>
          </div>
        )}

        {/* 종목 미선택 */}
        {!activeStock && favoriteStocks.length > 0 && (
          <div style={{ textAlign: 'center', padding: '40px 20px', color: '#888' }}>위에서 종목을 선택해주세요.</div>
        )}

        {/* 주식 시세 카드 */}
        {activeStock && (
          <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', marginBottom: '20px', boxShadow: '0 2px 5px rgba(0,0,0,0.08)', textAlign: 'center' }}>
            <h2 style={{ margin: '0 0 10px 0', fontSize: '1.2rem', color: '#202124' }}>
              {activeStock.name}
              <span style={{ fontSize: '0.85rem', color: '#888', fontWeight: 'normal', marginLeft: '6px' }}>({activeStock.ticker})</span>
            </h2>
            {stockDetail ? (
              <div>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#202124', marginBottom: '5px' }}>
                  {stockDetail.price?.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 2 })}
                </div>
                <div style={{ fontSize: '1.1rem', fontWeight: 'bold', color: stockDetail.diff > 0 ? '#d93025' : stockDetail.diff < 0 ? '#1a73e8' : '#5f6368' }}>
                  {stockDetail.diff > 0 ? '▲' : stockDetail.diff < 0 ? '▼' : '-'}{' '}
                  {Math.abs(stockDetail.diff)?.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 2 })}{' '}
                  ({stockDetail.diff > 0 ? '+' : ''}{stockDetail.diff_percent}%)
                </div>
              </div>
            ) : (
              <div style={{ color: '#aaa', fontSize: '0.9rem' }}>시세 정보를 불러오는 중...</div>
            )}
          </div>
        )}

        {/* 관련 뉴스 */}
        {isLoading ? (
          <div style={{ textAlign: 'center', padding: '50px', color: '#888' }}>로딩 중...</div>
        ) : (
          <>
            {newsList.length > 0 && (
              <h3 style={{ fontSize: '1rem', color: '#137333', marginBottom: '12px', marginTop: 0 }}>
                📰 {activeStock?.name} 관련 최신 뉴스
              </h3>
            )}
            {newsList.map((news) => (
              <div key={news.id} onClick={() => openNewsLink(news.url)}
                style={{ backgroundColor: 'white', padding: '15px', borderRadius: '12px', marginBottom: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)', cursor: 'pointer', transition: 'box-shadow 0.2s' }}
                onMouseEnter={e => e.currentTarget.style.boxShadow = '0 3px 8px rgba(0,0,0,0.15)'}
                onMouseLeave={e => e.currentTarget.style.boxShadow = '0 1px 3px rgba(0,0,0,0.08)'}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <span style={{ fontSize: '0.75rem', color: '#137333', fontWeight: 'bold' }}>
                    {ALL_CATEGORIES.find(c => c.id === news.category_code)?.name || '관련뉴스'}
                  </span>
                  <span style={{ fontSize: '0.75rem', color: '#999' }}>{news.created_at}</span>
                </div>
                <h3 style={{ margin: '0 0 8px 0', fontSize: '1rem', color: '#202124', lineHeight: '1.4' }}>{news.title}</h3>
                <p style={{ margin: 0, fontSize: '0.875rem', color: '#5f6368', display: '-webkit-box', WebkitLineClamp: '2', WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                  {news.ai_summary}
                </p>
              </div>
            ))}
            {activeStock && newsList.length === 0 && !isLoading && (
              <div style={{ textAlign: 'center', padding: '30px', color: '#888' }}>해당 종목과 관련된 최근 뉴스가 없습니다.</div>
            )}
          </>
        )}
      </div>
    </div>
  );
}