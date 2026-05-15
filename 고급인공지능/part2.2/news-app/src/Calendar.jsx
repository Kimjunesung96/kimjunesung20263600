import React, { useState, useEffect } from 'react';

export default function Calendar() {
  // 1. 상태 관리
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]); // 현재 선택된 날짜 (YYYY-MM-DD)
  const [currentMonth, setCurrentMonth] = useState(new Date()); // 달력에 보여줄 '월' 관리
  const [schedules, setSchedules] = useState([]); // 선택된 날짜의 일정 목록
  const [newContent, setNewContent] = useState("");
  const [allMonthSchedules, setAllMonthSchedules] = useState({}); // 달력에 점(마커)을 찍기 위해 '이번 달'의 모든 일정 개수 저장
  const [dateInputText, setDateInputText] = useState(""); // 상단 텍스트 입력용 (ex: 20260513)

  // -----------------------------------------------------
  // 💡 [API] 선택한 '날짜'의 상세 일정 가져오기
  // -----------------------------------------------------
  const fetchSchedules = () => {
    fetch(`http://localhost:8000/api/schedule/${selectedDate}`)
      .then(res => res.json())
      .then(data => {
        if(data.status === "success") setSchedules(data.data);
      })
      .catch(err => console.error("일정 불러오기 실패:", err));
  };

  // -----------------------------------------------------
  // 💡 [API] '이번 달' 전체의 일정 유무 가져오기 (마커 표시용)
  // -----------------------------------------------------
  const fetchMonthSchedules = () => {
    // API에 /api/schedule/month/2026-05 같은 라우트가 아직 없으므로, 
    // 임시로 그냥 달력 UI를 위해 껍데기만 만들어 둡니다.
    // (완벽한 표시를 원하시면 파이썬 쪽에 API를 하나 더 파야 합니다. 지금은 빈 객체 유지)
    setAllMonthSchedules({});
  };

  // 날짜가 바뀔 때마다 실행
  useEffect(() => {
    fetchSchedules();
    setDateInputText(selectedDate.replace(/-/g, '')); // 2026-05-13 -> 20260513 자동 변경
    setCurrentMonth(new Date(selectedDate)); // 달력도 선택한 날짜의 달로 이동
  }, [selectedDate]);

  // 달(Month)이 바뀔 때마다 실행
  useEffect(() => {
    fetchMonthSchedules();
  }, [currentMonth.getMonth(), currentMonth.getFullYear()]);

  // -----------------------------------------------------
  // 💡 기능: 일정 등록/삭제
  // -----------------------------------------------------
  const handleAdd = () => {
    if(!newContent.trim()) return;
    fetch("http://localhost:8000/api/schedule", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ date: selectedDate, content: newContent })
    })
    .then(() => {
      setNewContent(""); 
      fetchSchedules(); 
      fetchMonthSchedules(); // 등록 후 달력 마커 업데이트
    });
  };

  const handleDelete = (id) => {
    fetch(`http://localhost:8000/api/schedule/${id}`, { method: "DELETE" })
      .then(() => {
        fetchSchedules();
        fetchMonthSchedules(); // 삭제 후 달력 마커 업데이트
      });
  };

  // -----------------------------------------------------
  // 💡 기능: 상단 텍스트로 날짜 검색 (ex: 20260513 치고 엔터)
  // -----------------------------------------------------
  const handleDateInputSubmit = () => {
    if (dateInputText.length === 8) {
      const year = dateInputText.substring(0, 4);
      const month = dateInputText.substring(4, 6);
      const day = dateInputText.substring(6, 8);
      const formattedDate = `${year}-${month}-${day}`;
      
      // 유효한 날짜인지 체크
      const parsedDate = new Date(formattedDate);
      if (!isNaN(parsedDate.getTime())) {
        setSelectedDate(formattedDate);
      } else {
        alert("유효하지 않은 날짜입니다.");
        setDateInputText(selectedDate.replace(/-/g, '')); // 원상복구
      }
    } else {
      alert("YYYYMMDD 형식(8자리 숫자)으로 입력해주세요. (예: 20260513)");
      setDateInputText(selectedDate.replace(/-/g, '')); // 원상복구
    }
  };


  // -----------------------------------------------------
  // 💡 [핵심] 달력 그리기 (이번 달의 날짜 박스들 계산)
  // -----------------------------------------------------
  const renderCalendarDays = () => {
    const year = currentMonth.getFullYear();
    const month = currentMonth.getMonth(); // 0 ~ 11

    // 이번 달 1일이 무슨 요일인지 (0:일, 1:월, ... 6:토)
    const firstDay = new Date(year, month, 1).getDay();
    // 이번 달이 며칠까지 있는지 (28, 29, 30, 31)
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    const days = [];
    
    // 1. 1일 이전의 빈 칸(저번 달 날짜 공간) 채우기
    for (let i = 0; i < firstDay; i++) {
      days.push(<div key={`empty-${i}`} style={{ padding: '10px', backgroundColor: '#f9f9f9', border: '1px solid #eee' }}></div>);
    }

    // 2. 실제 날짜 칸 채우기
    for (let i = 1; i <= daysInMonth; i++) {
      const dateString = `${year}-${String(month + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}`;
      const isSelected = dateString === selectedDate;
      const isToday = dateString === new Date().toISOString().split('T');
      const hasSchedule = allMonthSchedules[dateString] > 0; // 일정이 있는지 확인 (임시)

      days.push(
        <div 
          key={dateString} 
          onClick={() => setSelectedDate(dateString)}
          style={{ 
            padding: '10px 5px', 
            height: '60px', 
            border: isSelected ? '2px solid #1a73e8' : '1px solid #eee', 
            backgroundColor: isSelected ? '#e8f0fe' : (isToday ? '#fff8e1' : 'white'),
            cursor: 'pointer',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            position: 'relative'
          }}
        >
          {/* 날짜 숫자 */}
          <span style={{ fontWeight: isSelected || isToday ? 'bold' : 'normal', color: isSelected ? '#1a73e8' : '#202124' }}>
            {i}
          </span>
          {/* 💡 일정 있음 표시 (마커) - 지금은 프론트에서 임시로 작동 */}
          {(hasSchedule || schedules.length > 0 && isSelected) && (
            <div style={{ width: '6px', height: '6px', backgroundColor: '#ea4335', borderRadius: '50%', marginTop: '5px' }}></div>
          )}
        </div>
      );
    }

    // 3. 마지막 날짜 이후의 빈 칸 채우기 (마지막 주 완성)
    const totalSlots = days.length;
    const remainingSlots = 7 - (totalSlots % 7);
    if (remainingSlots < 7) {
      for (let i = 0; i < remainingSlots; i++) {
        days.push(<div key={`empty-end-${i}`} style={{ padding: '10px', backgroundColor: '#f9f9f9', border: '1px solid #eee' }}></div>);
      }
    }

    return days;
  };


  return (
    <div style={{ padding: '20px', backgroundColor: 'white', minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      
      {/* 💡 상단 컨트롤 패널: YYYYMMDD 입력 검색기 */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', backgroundColor: '#f8f9fa', padding: '15px', borderRadius: '12px', border: '1px solid #ddd' }}>
        <button 
          onClick={() => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1))}
          style={{ background: 'none', border: 'none', fontSize: '20px', cursor: 'pointer', fontWeight: 'bold', color: '#5f6368' }}
        >
          ◀
        </button>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <h2 style={{ fontSize: '18px', margin: 0, fontWeight: 'bold' }}>{currentMonth.getFullYear()}년 {currentMonth.getMonth() + 1}월</h2>
          <span style={{ color: '#ccc' }}>|</span>
          <input 
            type="text" 
            value={dateInputText}
            onChange={(e) => setDateInputText(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleDateInputSubmit()}
            placeholder="YYYYMMDD"
            maxLength={8}
            style={{ width: '100px', padding: '5px 10px', borderRadius: '5px', border: '1px solid #ccc', textAlign: 'center', fontWeight: 'bold', color: '#1a73e8' }}
          />
          <button onClick={handleDateInputSubmit} style={{ padding: '5px 10px', backgroundColor: '#1a73e8', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer', fontSize: '12px' }}>이동</button>
        </div>

        <button 
          onClick={() => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1))}
          style={{ background: 'none', border: 'none', fontSize: '20px', cursor: 'pointer', fontWeight: 'bold', color: '#5f6368' }}
        >
          ▶
        </button>
      </div>

      {/* 💡 펼쳐진 그리드 탁상 달력 */}
      <div style={{ marginBottom: '25px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)', borderRadius: '12px', overflow: 'hidden', border: '1px solid #eee' }}>
        {/* 요일 헤더 */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', backgroundColor: '#f1f3f4', textAlign: 'center', padding: '10px 0', fontWeight: 'bold', fontSize: '14px', borderBottom: '1px solid #ddd' }}>
          <div style={{ color: '#ea4335' }}>일</div>
          <div>월</div>
          <div>화</div>
          <div>수</div>
          <div>목</div>
          <div>금</div>
          <div style={{ color: '#1a73e8' }}>토</div>
        </div>
        {/* 날짜 칸들 (7열 그리드) */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', backgroundColor: 'white' }}>
          {renderCalendarDays()}
        </div>
      </div>


      {/* 💡 선택된 날짜의 일정 영역 */}
      <div style={{ flex: 1, backgroundColor: '#f8f9fa', padding: '15px', borderRadius: '12px', border: '1px solid #eee' }}>
        <h3 style={{ margin: '0 0 15px 0', fontSize: '16px', color: '#1a73e8' }}>
          📌 {selectedDate.split('-')[1]}월 {selectedDate.split('-')[2]}일 일정
        </h3>
        
        {/* 일정 추가 입력창 */}
        <div style={{ display: 'flex', gap: '8px', marginBottom: '15px' }}>
          <input
            type="text"
            value={newContent}
            onChange={(e) => setNewContent(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleAdd()}
            placeholder="이 날의 일정을 추가하세요..."
            style={{ flex: 1, padding: '10px', borderRadius: '6px', border: '1px solid #ccc', fontSize: '14px' }}
          />
          <button onClick={handleAdd} style={{ padding: '0 15px', backgroundColor: '#34a853', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>
            등록
          </button>
        </div>

        {/* 일정 리스트 출력 */}
        <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
          {schedules.length === 0 ? (
            <li style={{ textAlign: 'center', color: '#999', padding: '20px 0', fontSize: '14px' }}>등록된 일정이 없습니다.</li>
          ) : (
            schedules.map(sch => (
              <li key={sch.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px', backgroundColor: 'white', marginBottom: '8px', borderRadius: '6px', borderLeft: '4px solid #fbbc05', boxShadow: '0 1px 2px rgba(0,0,0,0.05)' }}>
                <span style={{ fontSize: '14px', color: '#202124' }}>{sch.content}</span>
                <button onClick={() => handleDelete(sch.id)} style={{ color: '#ea4335', background: 'none', border: 'none', cursor: 'pointer', fontSize: '16px', padding: '0 5px' }}>✖</button>
              </li>
            ))
          )}
        </ul>
      </div>

    </div>
  );
}