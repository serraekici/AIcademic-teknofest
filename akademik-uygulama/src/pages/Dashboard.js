import React, { useEffect, useState } from 'react';
import { jwtDecode } from 'jwt-decode';
import '../styles/Dashboard.css';
import Sidebar from '../components/Sidebar';
import logo from '../logo.svg';
import { useNavigate } from 'react-router-dom';


const Dashboard = () => {
  const [username, setUsername] = useState('');
  

const handleChatbotCardClick = () => {
  navigate("/chatbot-plan");
};

  const navigate = useNavigate();

  // Kullanıcı adı ve giriş kontrolü
  useEffect(() => {
    const token = localStorage.getItem("access");
    if (!token) {
      navigate("/login");
    } else {
      try {
        const decoded = jwtDecode(token);
        setUsername(decoded.username);
      } catch (error) {
        console.error("Token çözümlenemedi:", error);
        navigate("/login");
      }
    }
  }, [navigate]);

  const handleKaynakChatbotCardClick = () => {
    navigate("/kaynakchatbot");
} ;



  

  return (
    <div className="dashboard-container">
      <Sidebar />

      <div className="main-content">
        <div className="logo-section">
          <img src={logo} alt="Logo" className="main-logo" />
          <h2>Hoş geldin {username}!</h2>
      

        </div>
        
              <div className="chatbot-section">
        <div
          className="chatbot-card"
          onClick={handleChatbotCardClick}
          style={{ cursor: "pointer" }}
        >
          GPT Çalışma Planı Chatbotu
        </div>

        <div
          className="chatbot-card"
          onClick={handleKaynakChatbotCardClick}
          style={{ cursor: "pointer" }}
        >
          Kaynak Chatbot
        </div>
        
        <div className="chatbot-card">Chatbot 3</div>
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
