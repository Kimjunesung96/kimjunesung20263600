import { useState, useEffect, useCallback, useRef } from 'react';

const PAGE_SIZE = 10;

export function useNewsData({ activeTab, searchKeyword, homeMode, currentMenu, alarmInterval }) {
  const [newsList, setNewsList] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [offset, setOffset] = useState(0);
  const [lastUpdated, setLastUpdated] = useState(null);

  const alarmIntervalRef = useRef(alarmInterval);
  useEffect(() => { alarmIntervalRef.current = alarmInterval; }, [alarmInterval]);

  const isFetchingMoreRef = useRef(false);

  const buildNewsUrl = useCallback((currentOffset) => {
    if (searchKeyword)
      return `http://localhost:8000/api/search?q=${encodeURIComponent(searchKeyword)}&limit=${PAGE_SIZE}&offset=${currentOffset}`;
    return `http://localhost:8000/api/news/${activeTab}?limit=${PAGE_SIZE}&offset=${currentOffset}`;
  }, [activeTab, searchKeyword]);

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
        if (result.status === 'success') {
          setNewsList(result.data);
          setOffset(result.data.length);
          setHasMore(result.data.length === PAGE_SIZE);
          setLastUpdated(new Date());
        }
        if (!isBackground) setIsLoading(false);
      })
      .catch(err => { console.error(err); if (!isBackground) setIsLoading(false); });
  }, [buildNewsUrl]);

  const fetchMoreNews = useCallback(() => {
    if (isFetchingMoreRef.current || !hasMore || homeMode !== 'news') return;
    isFetchingMoreRef.current = true;
    setIsLoadingMore(true);

    fetch(buildNewsUrl(offset))
      .then(res => res.json())
      .then(result => {
        if (result.status === 'success') {
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

  // 탭/검색어 바뀔 때 자동 갱신
  useEffect(() => {
    if (currentMenu !== 'home' || homeMode !== 'news') return;
    fetchNews(false);
    const intervalMs = alarmIntervalRef.current * 60 * 1000;
    const intervalId = setInterval(() => fetchNews(true), intervalMs);
    return () => clearInterval(intervalId);
  }, [activeTab, currentMenu, searchKeyword, homeMode, fetchNews]);

  return {
    newsList,
    setNewsList,
    isLoading,
    isLoadingMore,
    hasMore,
    lastUpdated,
    setLastUpdated,
    fetchNews,
    fetchMoreNews,
  };
}