import React, { useEffect, useState } from 'react';
import {jwtDecode} from 'jwt-decode';
import '../styles/Dashboard.css';
import Sidebar from '../components/Sidebar';
import logo from '../logo.svg';
import { useNavigate } from 'react-router-dom';

const Dashboard = () => {
  const [username, setUsername] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("access");
    if (!token) {
      navigate("/login");
    } else {
      try {
        const decoded = jwtDecode(token);
        setUsername(decoded.username); // token'dan kullanıcı adı çek
      } catch (error) {
        console.error("Token çözümlenemedi:", error);
        navigate("/login");
      }
    }
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    navigate("/login");
  };

  return (
    <div className="dashboard-container">
      <Sidebar />

      <div className="main-content">
        <div className="logo-section">
          <img src={logo} alt="Logo" className="main-logo" />
          <h2>Hoş geldin {username}!</h2> {/* ✅ Kullanıcı adı burada gösterilir */}
        </div>

        <div className="chatbot-section">
          <div className="chatbot-card">Chatbot 1</div>
          <div className="chatbot-card">Chatbot 2</div>
          <div className="chatbot-card">Chatbot 3</div>
        </div>

        <div className="schedule-section">
          <table className="schedule-table">
            <thead>
              <tr>
                <th>Time/Day</th>
                {[...Array(7)].map((_, i) => (
                  <th key={i}>Day {i + 1}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {[...Array(3)].map((_, row) => (
                <tr key={row}>
                  <td>Row {row + 1}</td>
                  {[...Array(7)].map((_, col) => (
                    <td key={col}></td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="right-section">
        <div className="calendar">📅 Takvim</div>
        <div className="events">📌 Etkinlikler</div>
      </div>
    </div>
  );
};

export default Dashboard;
