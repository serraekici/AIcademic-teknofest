import React from 'react';
import '../styles/Sidebar.css';
import { useNavigate } from 'react-router-dom';

const Sidebar = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('user');
    navigate('/login');
  };

  return (
    <div className="sidebar">
      <div className="user-info">
        <div className="user-avatar">👤</div>
        <div className="user-name">Kullanıcı Adı</div>
      </div>
      <ul className="sidebar-menu">
        <li>⭐ Favoriler</li>
        <li onClick={handleLogout}>🚪 Çıkış Yap</li>
      </ul>
    </div>
  );
};

export default Sidebar;
