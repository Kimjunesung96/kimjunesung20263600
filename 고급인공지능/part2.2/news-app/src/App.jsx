import { useState, useEffect, useCallback, useRef } from 'react'
import Calendar from './Calendar'; 
import Clipboard from './Clipboard';

const ALL_CATEGORIES = [
  { id: '01', name: 'IT/테크' }, { id: '02', name: '경제' },
  { id: '03', name: '사회' }, { id: '04', name: '세계' },
  { id: '05', name: '연예' }, { id: '06', name: '스포츠' },
  { id: '07', name: '과학' }, { id: '08', name: '건강' },
];

const PAGE_SIZE = 10; // 한 번에 가져올 뉴스 수

export default function App() {
  const [homeMode, setHomeMode] = useState('news'); 

  const [activeTab, setActiveTab] = useState('01'); 
  const [newsList, setNewsList] = useState([]); 
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingMore, setIsLoadingMore] = useState(false); // ✅ 추가 로딩용
  const [hasMore, setHasMore] = useState(true);              // ✅ 더 불러올 게 있는지
  const [offset, setOffset] = useState(0);                   // ✅ 현재 offset
  const [currentMenu, setCurrentMenu] = useState('home');
  
  const [searchKeyword, setSearchKeyword] = useState("");

  const [alarmInterval, setAlarmInterval] = useState(10);
  const [enabledCategories, setEnabledCategories] = useState(['01', '02', '03']);
  const [bubbleDuration, setBubbleDuration] = useState(5);
  const [newsCount, setNewsCount] = useState(10);

  const [favoriteStocks, setFavoriteStocks] = useState([]);
  const [newStockName, setNewStockName] = useState("");
  const [searchResults, setSearchResults] = useState([]); 

  const [activeStock, setActiveStock] = useState(null);
  const [stockDetail, setStockDetail] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const alarmIntervalRef = useRef(alarmInterval);
  useEffect(() => { alarmIntervalRef.current = alarmInterval; }, [alarmInterval]);

  // ✅ 스크롤 감지용 ref
  const scrollContainerRef = useRef(null);
  const isFetchingMoreRef = useRef(false); // 중복 요청 방지

  // ─── URL 쿼리 파라미터로 검색어 처리 ───
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const query = params.get('search');
    if (query) {
      setSearchKeyword(query);
      setActiveTab('search'); 
      setHomeMode('news'); 
    }
  }, []);

  // ─── 초기 설정 + 주식 목록 로드 ───
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
      .then(data => { 
        if (data.status === 'success') {
          setFavoriteStocks(data.data);
          setActiveStock(prev => {
            if (prev) return prev;
            return data.data.length > 0 ? data.data[0] : null;
          });
        }
      });
  };

  // ─────────────────────────────────────────────────────────
  // ✅ URL 생성 헬퍼
  // ─────────────────────────────────────────────────────────
  const buildNewsUrl = useCallback((currentOffset) => {
    if (searchKeyword)
      return `http://localhost:8000/api/search?q=${encodeURIComponent(searchKeyword)}&limit=${PAGE_SIZE}&offset=${currentOffset}`;
    return `http://localhost:8000/api/news/${activeTab}?limit=${PAGE_SIZE}&offset=${currentOffset}`;
  }, [activeTab, searchKeyword]);

  // ─────────────────────────────────────────────────────────
  // ✅ 뉴스 최초 로드 (탭/검색어 바뀔 때)
  // ─────────────────────────────────────────────────────────
  const fetchNews = useCallback((isBackground = false) => {
    if (!isBackground) {
      setIsLoading(true);
      setNewsList([]);
      setOffset(0);
      setHasMore(true);
    }
    fetch(buildNewsUrl(0))
      .then(res => res.json())
      .then(result => {
        if (result.status === "success") {
          setNewsList(result.data);
          setOffset(result.data.length);
          setHasMore(result.data.length === PAGE_SIZE);
          setLastUpdated(new Date());
        }
        if (!isBackground) setIsLoading(false);
      })
      .catch(err => { console.error(err); if (!isBackground) setIsLoading(false); });
  }, [buildNewsUrl]);

  // ─────────────────────────────────────────────────────────
  // ✅ 추가 뉴스 로드 (스크롤 바닥 도달 시)
  // ─────────────────────────────────────────────────────────
  const fetchMoreNews = useCallback(() => {
    if (isFetchingMoreRef.current || !hasMore || homeMode !== 'news') return;
    isFetchingMoreRef.current = true;
    setIsLoadingMore(true);

    fetch(buildNewsUrl(offset))
      .then(res => res.json())
      .then(result => {
        if (result.status === "success") {
          setNewsList(prev => [...prev, ...result.data]);
          setOffset(prev => prev + result.data.length);
          setHasMore(result.data.length === PAGE_SIZE);
        }
      })
      .catch(err => console.error(err))
      .finally(() => {
        setIsLoadingMore(false);
        isFetchingMoreRef.current = false;
      });
  }, [buildNewsUrl, offset, hasMore, homeMode]);

  // ─────────────────────────────────────────────────────────
  // ✅ 스크롤 이벤트 감지
  // ─────────────────────────────────────────────────────────
  useEffect(() => {
    const el = scrollContainerRef.current;
    if (!el) return;

    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = el;
      // 바닥에서 150px 이내면 추가 로드
      if (scrollHeight - scrollTop - clientHeight < 150) {
        fetchMoreNews();
      }
    };

    el.addEventListener('scroll', handleScroll);
    return () => el.removeEventListener('scroll', handleScroll);
  }, [fetchMoreNews]);

  // ─────────────────────────────────────────────────────────
  // ✅ 뉴스 탭 자동 갱신
  // ─────────────────────────────────────────────────────────
  useEffect(() => {
    if (currentMenu !== 'home' || homeMode !== 'news') return;
    fetchNews(false);
    const intervalMs = alarmIntervalRef.current * 60 * 1000;
    const intervalId = setInterval(() => fetchNews(true), intervalMs);
    return () => clearInterval(intervalId);
  }, [activeTab, currentMenu, searchKeyword, homeMode, fetchNews]);

  // ─────────────────────────────────────────────────────────
  // ✅ 주식 탭
  // ─────────────────────────────────────────────────────────
  const fetchStockData = useCallback((isBackground = false) => {
    if (!activeStock?.ticker) return;
    if (!isBackground) {
      setIsLoading(true);
      setStockDetail(null);
      setNewsList([]);
      setHasMore(false);
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
        if (result.status === "success") {
          setNewsList(result.data);
          setLastUpdated(new Date());
        }
        if (!isBackground) setIsLoading(false);
      })
      .catch(() => { if (!isBackground) setIsLoading(false); });
  }, [activeStock]);

  useEffect(() => {
    if (currentMenu !== 'home' || homeMode !== 'stock' || !activeStock?.ticker) return;
    fetchStockData(false);
    const intervalId = setInterval(() => fetchStockData(true), 30 * 1000);
    return () => clearInterval(intervalId);
  }, [activeStock, currentMenu, homeMode, fetchStockData]);

  // ─────────────────────────────────────────────────────────
  // ✅ 홈 탭으로 돌아올 때 즉시 갱신
  // ─────────────────────────────────────────────────────────
  const prevMenuRef = useRef(currentMenu);
  useEffect(() => {
    if (prevMenuRef.current !== 'home' && currentMenu === 'home') {
      if (homeMode === 'news') fetchNews(false);
      else if (homeMode === 'stock') fetchStockData(false);
    }
    prevMenuRef.current = currentMenu;
  }, [currentMenu, homeMode, fetchNews, fetchStockData]);

  const openNewsLink = (url) => window.open(url, '_blank');

  const saveAllSettings = (newInterval, newCategories, newDuration, newCount) => {
    fetch("http://localhost:8000/api/settings", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ alarm_interval: newInterval, enabled_categories: newCategories, bubble_duration: parseInt(newDuration) || 0, news_count: parseInt(newCount) || 0 })
    });
  };
  const handleIntervalChange = (val) => {
    const parsed = parseInt(val);
    setAlarmInterval(parsed);
    alarmIntervalRef.current = parsed;
    saveAllSettings(parsed, enabledCategories, bubbleDuration, newsCount);
  };
  const handleCategoryToggle = (id) => {
    const next = enabledCategories.includes(id) ? enabledCategories.filter(c => c !== id) : [...enabledCategories, id];
    if (next.length === 0) return;
    setEnabledCategories(next); saveAllSettings(alarmInterval, next, bubbleDuration, newsCount);
  };
  const handleDurationChange = (val) => { setBubbleDuration(val); saveAllSettings(alarmInterval, enabledCategories, val, newsCount); };
  const handleCountChange = (val) => { setNewsCount(val); saveAllSettings(alarmInterval, enabledCategories, bubbleDuration, val); };

  const handleSearchChange = (val) => {
    setNewStockName(val);
    if (!val.trim()) { setSearchResults([]); return; }
    fetch(`http://localhost:8000/api/search_stock?name=${encodeURIComponent(val)}`)
      .then(res => res.json())
      .then(data => { if (data.status === 'success') setSearchResults(data.data); })
      .catch(() => setSearchResults([]));
  };
  const handleSelectAndAdd = (stockName, stockTicker) => { setNewStockName(""); setSearchResults([]); handleAddStock(stockName, stockTicker); };
  const handleAddStock = (targetName = newStockName, targetTicker = "") => {
    if (!targetName.trim()) return alert("종목명을 입력해주세요!");
    const btn = document.getElementById("addStockBtn");
    if(btn) { btn.innerText = "추가 중..."; btn.disabled = true; }
    fetch("http://localhost:8000/api/favorites", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: targetName.trim(), ticker: targetTicker }) 
    }).then(res => res.json()).then(data => {
      if(data.status === 'success') { fetchStocks(); setNewStockName(""); setSearchResults([]); }
      else alert("❌ " + data.message); 
    }).finally(() => { if(btn) { btn.innerText = "추가"; btn.disabled = false; } });
  };
  const handleDeleteStock = (id) => {
    if(window.confirm("이 종목을 삭제할까요?")) {
      fetch(`http://localhost:8000/api/favorites/${id}`, { method: "DELETE" }).then(() => {
        setActiveStock(prev => (prev?.id === id ? null : prev));
        fetchStocks();
      });
    }
  };

  const handleSwitchToStock = () => {
    setHomeMode('stock');
    setSearchKeyword("");
    if (!activeStock && favoriteStocks.length > 0) setActiveStock(favoriteStocks[0]);
  };

  const formatLastUpdated = (date) => {
    if (!date) return null;
    return date.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  };

  return (
    <div style={{ maxWidth: '500px', margin: '0 auto', backgroundColor: '#f5f5f5', minHeight: '100vh', display: 'flex', flexDirection: 'column', fontFamily: "'맑은 고딕', sans-serif" }}>
      
      {/* ── 헤더 ── */}
      <div style={{ backgroundColor: '#1a73e8', color: 'white', paddingTop: '15px', textAlign: 'center', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        <h1 style={{ margin: 0, fontSize: '1.5rem', marginBottom: '4px' }}>AI 뉴스 큐레이터</h1>
        <p style={{ margin: '0 0 0 0', fontSize: '0.8rem', opacity: 0.8 }}>실시간 주요 뉴스 브리핑</p>
        
        {currentMenu === 'home' && (
          <div style={{ display: 'flex', padding: '0 15px', marginTop: '10px' }}>
            <div onClick={() => setHomeMode('news')}
              style={{ flex: 1, padding: '10px 0', fontWeight: 'bold', cursor: 'pointer', borderBottom: homeMode === 'news' ? '3px solid white' : '3px solid transparent', color: homeMode === 'news' ? 'white' : 'rgba(255,255,255,0.6)', transition: 'all 0.2s' }}>
              📰 주요 뉴스
            </div>
            <div onClick={handleSwitchToStock}
              style={{ flex: 1, padding: '10px 0', fontWeight: 'bold', cursor: 'pointer', borderBottom: homeMode === 'stock' ? '3px solid white' : '3px solid transparent', color: homeMode === 'stock' ? 'white' : 'rgba(255,255,255,0.6)', transition: 'all 0.2s' }}>
              📈 관심 주식
            </div>
          </div>
        )}
      </div>

      {currentMenu === 'home' && (
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
          
          {/* ── 카테고리 / 종목 버튼 바 ── */}
          <div style={{ display: 'flex', overflowX: 'auto', padding: '10px', gap: '8px', backgroundColor: 'white', whiteSpace: 'nowrap', borderBottom: '1px solid #ddd', flexShrink: 0 }}>
            {homeMode === 'news' && ALL_CATEGORIES
              .filter(cat => enabledCategories.includes(cat.id))
              .map(cat => (
                <button key={cat.id} 
                  onClick={() => { setSearchKeyword(""); setActiveTab(cat.id); window.history.pushState({}, '', '/'); }} 
                  style={{ padding: '8px 16px', borderRadius: '20px', border: 'none', backgroundColor: activeTab === cat.id && !searchKeyword ? '#1a73e8' : '#f1f3f4', color: activeTab === cat.id && !searchKeyword ? 'white' : '#5f6368', fontWeight: 'bold', cursor: 'pointer', transition: 'all 0.2s', flexShrink: 0 }}>
                  {cat.name}
                </button>
              ))
            }
            {homeMode === 'stock' && favoriteStocks.length > 0 && favoriteStocks.map(stock => (
              <button key={stock.id} onClick={() => setActiveStock(stock)} 
                style={{ padding: '8px 16px', borderRadius: '20px', border: 'none', backgroundColor: activeStock?.id === stock.id ? '#34a853' : '#e6f4ea', color: activeStock?.id === stock.id ? 'white' : '#137333', fontWeight: 'bold', cursor: 'pointer', transition: 'all 0.2s', flexShrink: 0 }}>
                {stock.name}
              </button>
            ))}
            {homeMode === 'stock' && favoriteStocks.length === 0 && (
              <span style={{ color: '#888', fontSize: '0.85rem', padding: '8px 5px' }}>⚙️ 설정에서 관심 종목을 먼저 등록해주세요.</span>
            )}
          </div>

          {/* ── ✅ 스크롤 컨테이너 (이 div가 스크롤 감지 대상) ── */}
          <div
            ref={scrollContainerRef}
            style={{ flex: 1, padding: '15px', overflowY: 'auto' }}
          >
            
            {/* 갱신 시간 + 새로고침 */}
            {(homeMode === 'news' || (homeMode === 'stock' && activeStock)) && (
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <span style={{ fontSize: '0.75rem', color: '#aaa' }}>
                  {lastUpdated ? `🕐 ${formatLastUpdated(lastUpdated)} 갱신` : ''}
                </span>
                <button onClick={() => homeMode === 'news' ? fetchNews(false) : fetchStockData(false)}
                  style={{ fontSize: '0.75rem', padding: '4px 10px', backgroundColor: '#f1f3f4', border: '1px solid #ddd', borderRadius: '12px', cursor: 'pointer', color: '#5f6368' }}>
                  🔄 새로고침
                </button>
              </div>
            )}

            {/* 검색 결과 배너 */}
            {homeMode === 'news' && searchKeyword && (
              <div style={{ padding: '15px', marginBottom: '15px', backgroundColor: '#e8f0fe', color: '#1a73e8', fontWeight: 'bold', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderRadius: '12px' }}>
                <span>🔍 '{searchKeyword}' 검색 결과</span>
                <button onClick={() => { setSearchKeyword(""); setActiveTab('01'); window.history.pushState({}, '', '/'); }} 
                  style={{ padding: '5px 15px', backgroundColor: 'white', border: '1px solid #1a73e8', color: '#1a73e8', borderRadius: '15px', cursor: 'pointer' }}>
                  초기화
                </button>
              </div>
            )}

            {/* 주식 시세 카드 */}
            {homeMode === 'stock' && activeStock && (
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

            {homeMode === 'stock' && !activeStock && favoriteStocks.length > 0 && (
              <div style={{ textAlign: 'center', padding: '40px 20px', color: '#888' }}>위에서 종목을 선택해주세요.</div>
            )}

            {/* 초기 로딩 */}
            {isLoading ? (
              <div style={{ textAlign: 'center', padding: '50px', color: '#888' }}>로딩 중...</div>
            ) : (
              <>
                {homeMode === 'stock' && newsList.length > 0 && (
                  <h3 style={{ fontSize: '1rem', color: '#137333', marginBottom: '12px', marginTop: 0 }}>
                    📰 {activeStock?.name} 관련 최신 뉴스
                  </h3>
                )}

                {/* 뉴스 카드 목록 */}
                {newsList.map((news) => (
                  <div key={news.id} onClick={() => openNewsLink(news.url)} 
                    style={{ backgroundColor: 'white', padding: '15px', borderRadius: '12px', marginBottom: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)', cursor: 'pointer', transition: 'box-shadow 0.2s' }}
                    onMouseEnter={e => e.currentTarget.style.boxShadow = '0 3px 8px rgba(0,0,0,0.15)'}
                    onMouseLeave={e => e.currentTarget.style.boxShadow = '0 1px 3px rgba(0,0,0,0.08)'}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <span style={{ fontSize: '0.75rem', color: homeMode === 'stock' ? '#137333' : '#1a73e8', fontWeight: 'bold' }}>
                        {homeMode === 'stock'
                          ? (ALL_CATEGORIES.find(c => c.id === news.category_code)?.name || '관련뉴스')
                          : ALL_CATEGORIES.find(c => c.id === news.category_code)?.name}
                      </span>
                      <span style={{ fontSize: '0.75rem', color: '#999' }}>{news.created_at}</span>
                    </div>
                    <h3 style={{ margin: '0 0 8px 0', fontSize: '1rem', color: '#202124', lineHeight: '1.4' }}>{news.title}</h3>
                    <p style={{ margin: 0, fontSize: '0.875rem', color: '#5f6368', display: '-webkit-box', WebkitLineClamp: '2', WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                      {news.ai_summary}
                    </p>
                  </div>
                ))}

                {/* ✅ 추가 로딩 스피너 */}
                {isLoadingMore && (
                  <div style={{ textAlign: 'center', padding: '20px', color: '#aaa', fontSize: '0.85rem' }}>
                    ⏳ 뉴스 더 불러오는 중...
                  </div>
                )}

                {/* ✅ 더 이상 없을 때 */}
                {!hasMore && newsList.length > 0 && !isLoadingMore && (
                  <div style={{ textAlign: 'center', padding: '20px', color: '#ccc', fontSize: '0.8rem' }}>
                    ── 모든 뉴스를 불러왔습니다 ──
                  </div>
                )}

                {homeMode === 'stock' && activeStock && newsList.length === 0 && !isLoading && (
                  <div style={{ textAlign: 'center', padding: '30px', color: '#888' }}>해당 종목과 관련된 최근 뉴스가 없습니다.</div>
                )}
                {homeMode === 'news' && newsList.length === 0 && !isLoading && (
                  <div style={{ textAlign: 'center', padding: '30px', color: '#888' }}>뉴스가 없습니다.</div>
                )}
              </>
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
                  <span><strong>{stock.name}</strong>{' '}<span style={{ color: '#888', fontSize: '0.85rem' }}>({stock.ticker})</span></span>
                  <button onClick={() => handleDeleteStock(stock.id)} style={{ color: '#ea4335', background: 'none', border: 'none', cursor: 'pointer', fontSize: '0.9rem' }}>✖ 삭제</button>
                </li>
              ))}
              {favoriteStocks.length === 0 && (
                <li style={{ textAlign: 'center', color: '#999', padding: '15px' }}>등록된 종목이 없습니다.</li>
              )}
            </ul>
          </div>
        </div>
      )}

      {/* ── 하단 네비게이션 ── */}
      <div style={{ display: 'flex', borderTop: '1px solid #ddd', backgroundColor: 'white', position: 'sticky', bottom: 0, padding: '5px 0', flexShrink: 0 }}>
        <div onClick={() => setCurrentMenu('home')} style={{ flex: 1, textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px', color: currentMenu === 'home' ? '#1a73e8' : '#9aa0a6', cursor: 'pointer' }}>
          <span style={{ fontSize: '20px' }}>🏠</span>
          <span style={{ fontSize: '11px', fontWeight: currentMenu === 'home' ? 'bold' : 'normal' }}>홈</span>
        </div>
        <div onClick={() => setCurrentMenu('calendar')} style={{ flex: 1, textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px', color: currentMenu === 'calendar' ? '#1a73e8' : '#9aa0a6', cursor: 'pointer' }}>
          <span style={{ fontSize: '20px' }}>📅</span>
          <span style={{ fontSize: '11px', fontWeight: currentMenu === 'calendar' ? 'bold' : 'normal' }}>달력</span>
        </div>
        <div onClick={() => setCurrentMenu('clipboard')} style={{ flex: 1, textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px', color: currentMenu === 'clipboard' ? '#1a73e8' : '#9aa0a6', cursor: 'pointer' }}>
          <span style={{ fontSize: '20px' }}>📋</span>
          <span style={{ fontSize: '11px', fontWeight: currentMenu === 'clipboard' ? 'bold' : 'normal' }}>클립보드</span>
        </div>
        <div onClick={() => setCurrentMenu('settings')} style={{ flex: 1, textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px', color: currentMenu === 'settings' ? '#1a73e8' : '#9aa0a6', cursor: 'pointer' }}>
          <span style={{ fontSize: '20px' }}>⚙️</span>
          <span style={{ fontSize: '11px', fontWeight: currentMenu === 'settings' ? 'bold' : 'normal' }}>설정</span>
        </div>
      </div>
    </div>
  )
}