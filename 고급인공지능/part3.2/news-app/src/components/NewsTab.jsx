import { useRef, useEffect } from 'react';
import { useNewsData } from '../hooks/useNewsData';

const ALL_CATEGORIES = [
  { id: '01', name: 'IT/테크' }, { id: '02', name: '경제' },
  { id: '03', name: '사회' },   { id: '04', name: '세계' },
  { id: '05', name: '연예' },   { id: '06', name: '스포츠' },
  { id: '07', name: '과학' },   { id: '08', name: '건강' },
];

export default function NewsTab({
  activeTab, setActiveTab,
  searchKeyword, setSearchKeyword,
  enabledCategories,
  alarmInterval,
  currentMenu,
}) {
  const scrollContainerRef = useRef(null);

  const {
    newsList,
    isLoading,
    isLoadingMore,
    hasMore,
    lastUpdated,
    fetchNews,
    fetchMoreNews,
  } = useNewsData({
    activeTab,
    searchKeyword,
    homeMode: 'news',
    currentMenu,
    alarmInterval,
  });

  // 스크롤 바닥 감지 → 추가 로드
  useEffect(() => {
    const el = scrollContainerRef.current;
    if (!el) return;
    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = el;
      if (scrollHeight - scrollTop - clientHeight < 150) fetchMoreNews();
    };
    el.addEventListener('scroll', handleScroll);
    return () => el.removeEventListener('scroll', handleScroll);
  }, [fetchMoreNews]);

  const formatLastUpdated = (date) => {
    if (!date) return null;
    return date.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  };

  const openNewsLink = (url) => window.open(url, '_blank');

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>

      {/* 카테고리 버튼 바 */}
      <div style={{ display: 'flex', overflowX: 'auto', padding: '10px', gap: '8px', backgroundColor: 'white', whiteSpace: 'nowrap', borderBottom: '1px solid #ddd', flexShrink: 0 }}>
        {ALL_CATEGORIES
          .filter(cat => enabledCategories.includes(cat.id))
          .map(cat => (
            <button key={cat.id}
              onClick={() => { setSearchKeyword(''); setActiveTab(cat.id); window.history.pushState({}, '', '/'); }}
              style={{ padding: '8px 16px', borderRadius: '20px', border: 'none', backgroundColor: activeTab === cat.id && !searchKeyword ? '#1a73e8' : '#f1f3f4', color: activeTab === cat.id && !searchKeyword ? 'white' : '#5f6368', fontWeight: 'bold', cursor: 'pointer', transition: 'all 0.2s', flexShrink: 0 }}>
              {cat.name}
            </button>
          ))
        }
      </div>

      {/* 스크롤 컨테이너 */}
      <div ref={scrollContainerRef} style={{ flex: 1, padding: '15px', overflowY: 'auto' }}>

        {/* 갱신 시간 + 새로고침 */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
          <span style={{ fontSize: '0.75rem', color: '#aaa' }}>
            {lastUpdated ? `🕐 ${formatLastUpdated(lastUpdated)} 갱신` : ''}
          </span>
          <button onClick={() => fetchNews(false)}
            style={{ fontSize: '0.75rem', padding: '4px 10px', backgroundColor: '#f1f3f4', border: '1px solid #ddd', borderRadius: '12px', cursor: 'pointer', color: '#5f6368' }}>
            🔄 새로고침
          </button>
        </div>

        {/* 검색 결과 배너 */}
        {searchKeyword && (
          <div style={{ padding: '15px', marginBottom: '15px', backgroundColor: '#e8f0fe', color: '#1a73e8', fontWeight: 'bold', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderRadius: '12px' }}>
            <span>🔍 '{searchKeyword}' 검색 결과</span>
            <button onClick={() => { setSearchKeyword(''); setActiveTab('01'); window.history.pushState({}, '', '/'); }}
              style={{ padding: '5px 15px', backgroundColor: 'white', border: '1px solid #1a73e8', color: '#1a73e8', borderRadius: '15px', cursor: 'pointer' }}>
              초기화
            </button>
          </div>
        )}

        {/* 로딩 */}
        {isLoading ? (
          <div style={{ textAlign: 'center', padding: '50px', color: '#888' }}>로딩 중...</div>
        ) : (
          <>
            {/* 뉴스 카드 목록 */}
            {newsList.map((news) => (
              <div key={news.id} onClick={() => openNewsLink(news.url)}
                style={{ backgroundColor: 'white', padding: '15px', borderRadius: '12px', marginBottom: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)', cursor: 'pointer', transition: 'box-shadow 0.2s' }}
                onMouseEnter={e => e.currentTarget.style.boxShadow = '0 3px 8px rgba(0,0,0,0.15)'}
                onMouseLeave={e => e.currentTarget.style.boxShadow = '0 1px 3px rgba(0,0,0,0.08)'}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <span style={{ fontSize: '0.75rem', color: '#1a73e8', fontWeight: 'bold' }}>
                    {ALL_CATEGORIES.find(c => c.id === news.category_code)?.name}
                  </span>
                  <span style={{ fontSize: '0.75rem', color: '#999' }}>{news.created_at}</span>
                </div>
                <h3 style={{ margin: '0 0 8px 0', fontSize: '1rem', color: '#202124', lineHeight: '1.4' }}>{news.title}</h3>
                <p style={{ margin: 0, fontSize: '0.875rem', color: '#5f6368', display: '-webkit-box', WebkitLineClamp: '2', WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                  {news.ai_summary}
                </p>
              </div>
            ))}

            {/* 추가 로딩 스피너 */}
            {isLoadingMore && (
              <div style={{ textAlign: 'center', padding: '20px', color: '#aaa', fontSize: '0.85rem' }}>
                ⏳ 뉴스 더 불러오는 중...
              </div>
            )}

            {/* 끝 표시 */}
            {!hasMore && newsList.length > 0 && !isLoadingMore && (
              <div style={{ textAlign: 'center', padding: '20px', color: '#ccc', fontSize: '0.8rem' }}>
                ── 모든 뉴스를 불러왔습니다 ──
              </div>
            )}

            {newsList.length === 0 && !isLoading && (
              <div style={{ textAlign: 'center', padding: '30px', color: '#888' }}>뉴스가 없습니다.</div>
            )}
          </>
        )}
      </div>
    </div>
  );
}