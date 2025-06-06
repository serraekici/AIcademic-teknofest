import React from 'react';
import '../styles/Sidebar.css';
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
        <li>⭐ Favoriler</li>
        <li onClick={handleLogout}>🚪 Çıkış Yap</li>
           <div
          className="exam-calendar-card"
          onClick={() => navigate("/exam-schedule")}
          style={{ cursor: "pointer" }}
        >
          🗓️ Sınav Takvimi
        </div>
      </ul>
    </div>
  );
};

export default Sidebar;
