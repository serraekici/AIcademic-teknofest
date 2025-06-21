import React, { useEffect, useState } from 'react';
import '../styles/Sidebar.css';
import Calendar from 'react-calendar';
import 'react-calendar/dist/Calendar.css';
import { useNavigate } from 'react-router-dom';

const Sidebar = () => {
  const navigate = useNavigate();
  const [examDates, setExamDates] = useState([]);
  const username = localStorage.getItem('username');

  const handleLogout = () => {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    localStorage.removeItem('username');
    navigate('/login');
  };

  useEffect(() => {
    const token = localStorage.getItem("access");

    fetch("http://localhost:8000/api/user-exams/", {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json"
      }
    })
      .then(res => res.json())
      .then(data => {
        const formatted = data.map(exam => ({
          date: exam.exam_date,  // örnek: "2025-06-12"
          title: exam.course_name,
          time: exam.exam_time
        }));
        setExamDates(formatted);
      })
      .catch(err => console.error("Sınav verisi alınamadı:", err));
  }, []);

  const formatDate = (dateObj) => {
    return dateObj.toLocaleDateString('en-CA'); // YYYY-MM-DD formatı
  };

  return (
    <div className="sidebar">
      <div className="user-info">
        <div className="user-avatar">👤</div>
        <div className="user-name">{username || "Kullanıcı Adı"}</div>
      </div>

      <ul className="sidebar-menu">
        <li onClick={() => navigate("/favorites")} style={{ cursor: "pointer" }}>
          ⭐ Favoriler
        </li>
        <li onClick={() => navigate("/exam-schedule")} style={{ cursor: "pointer" }}>
          🗓️ Sınav Takvimi
        </li>
        <li onClick={handleLogout}>🚪 Çıkış Yap</li>
      </ul>

      <div className="sidebar-calendar">
        <Calendar
          value={new Date()}
          locale="tr-TR"
          showNeighboringMonth={false}
          tileClassName={({ date }) => {
            const formattedDate = formatDate(date);
            return examDates.some(e => e.date === formattedDate) ? 'exam-date' : null;
          }}
          tileContent={({ date }) => {
            const formattedDate = formatDate(date);
            const matches = examDates.filter(e => e.date === formattedDate);

            if (matches.length === 0) return null;

            return (
              <span
                title={matches.map(e => `${e.title} - ${e.time}`).join('\n')}
                style={{ display: "block", textAlign: "center", fontSize: "12px", color: "#8e24aa" }}
              >
                📌
              </span>
            );
          }}

        />
      </div>
    </div>
  );
};

export default Sidebar;
