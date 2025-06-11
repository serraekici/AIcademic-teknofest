import React, { useEffect, useState } from 'react';
import { jwtDecode } from 'jwt-decode';
import '../styles/Dashboard.css';
import Sidebar from '../components/Sidebar';
import logo from '../logo.svg';
import { useNavigate } from 'react-router-dom';

const Dashboard = () => {
  const [username, setUsername] = useState('');
  const [plan, setPlan] = useState("");

  const navigate = useNavigate();

  const handleChatbotCardClick = () => {
    navigate("/chatbot-plan");
  };

  const handleKaynakChatbotCardClick = () => {
    navigate("/kaynakchatbot");
  };

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

  // Çalışma planını localStorage'dan çek
  useEffect(() => {
    const storedPlan = localStorage.getItem("studyPlan");
    if (storedPlan) setPlan(storedPlan);
  }, []);

  // Planı sil
  const handleDeletePlan = () => {
    localStorage.removeItem("studyPlan");
    setPlan("");
  };

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

        {/* Çalışma Planı Kartı tam burada! */}
        <div style={{ margin: "10px 0 8px 0" }}>
          {plan ? (
            <div
              style={{
                border: "1px solid #ddd",
                borderRadius: 14,
                padding: 24,
                background: "#f8fafc",
                boxShadow: "0 2px 8px rgba(60,60,90,0.08)",
                maxHeight: 260,
                overflowY: "auto",
                position: "relative",
                marginBottom: 16,
                color: "#111"
              }}
            >
              <strong>Çalışma Planın:</strong>
              <div style={{ margin: "16px 0", whiteSpace: "pre-line" }}>{plan}</div>
              <button
                onClick={handleDeletePlan}
                style={{
                  position: "absolute",
                  top: 14,
                  right: 14,
                  border: "none",
                  background: "#ef4444",
                  color: "#fff",
                  borderRadius: 6,
                  padding: "4px 10px",
                  cursor: "pointer",
                  fontWeight: "bold"
                }}
              >
                Sil
              </button>
            </div>
          ) : (
            <div style={{ color: "#555", fontStyle: "italic" }}>
              Henüz bir çalışma planı yok.
            </div>
          )}
        </div>
      </div>

      <div className="right-section">
        <div className="calendar">📅 Takvim</div>
         <div className="events" style={{
          background: "#fff",
          borderRadius: 12,
          boxShadow: "0 2px 8px rgba(0,0,0,0.07)",
          padding: 16,
          marginTop: 12,
          minWidth: 280,
          maxWidth: 350,
          minHeight: 110,
          textAlign: "center"
        }}>
          <div style={{ fontWeight: "bold", fontSize: 17, marginBottom: 10 }}>
            📌 Etkinlikler
          </div>
          <button
            style={{
              padding: "10px 20px",
              background: "#2563eb",
              color: "#fff",
              border: "none",
              borderRadius: 6,
              cursor: "pointer",
              fontWeight: "bold",
              marginTop: 8
            }}
            onClick={() => navigate("/events")}
          >
            Tüm Etkinlikleri Gör
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;  