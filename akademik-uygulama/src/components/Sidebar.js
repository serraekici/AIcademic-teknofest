import React from 'react';
import '../styles/Sidebar.css';
import Calendar from 'react-calendar';
import 'react-calendar/dist/Calendar.css';
import { useNavigate } from 'react-router-dom';

const Sidebar = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    localStorage.removeItem('username');
    navigate('/login');
  };

  const username = localStorage.getItem('username');

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
          tileDisabled={() => true} // tıklamayı pasif yaparsan: opsiyonel
        />
      </div>

    </div>
    
  );
};

export default Sidebar;
