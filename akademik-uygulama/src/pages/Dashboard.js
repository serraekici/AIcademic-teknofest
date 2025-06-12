import React, { useEffect, useState } from 'react';
import { jwtDecode } from 'jwt-decode';
import '../styles/Dashboard.css';
import Sidebar from '../components/Sidebar';
import logo from '../logo.svg';
import { useNavigate } from 'react-router-dom';

const Dashboard = () => {
  const [username, setUsername] = useState('');
  const [plan, setPlan] = useState("");
  const [events, setEvents] = useState([]);

  const navigate = useNavigate();

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

  useEffect(() => {
    const storedPlan = localStorage.getItem("studyPlan");
    if (storedPlan) setPlan(storedPlan);
  }, []);

  const handleDeletePlan = () => {
    localStorage.removeItem("studyPlan");
    setPlan("");
  };

  useEffect(() => {
    fetch("http://localhost:8000/api/local-events/")
      .then(res => res.json())
      .then(data => setEvents(data))
      .catch(err => console.error("Etkinlik verisi alınamadı:", err));
  }, []);

  const emojis = {
    "Konser": "🎵",
    "Tiyatro": "🎭",
    "Festival": "🎉",
    "Sergi": "🖼️",
    "Workshop": "🛠️",
    "Genel": "📌"
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
          <div className="chatbot-card" onClick={() => navigate("/chatbot-plan")} style={{ cursor: "pointer" }}>
            GPT Çalışma Planı Chatbotu
          </div>
          <div className="chatbot-card" onClick={() => navigate("/kaynakchatbot")} style={{ cursor: "pointer" }}>
            Kaynak Chatbot
          </div>
          <div className="chatbot-card" onClick={() => navigate("/tercihchatbot")} style={{ cursor: "pointer" }}>
            Tercih Chatbotu
          </div>
        </div>

        <div style={{ margin: "10px 0 8px 0" }}>
          {plan ? (
            <div style={{
              border: "1px solid #ddd", borderRadius: 14, padding: 24, background: "#f8fafc",
              boxShadow: "0 2px 8px rgba(60,60,90,0.08)", maxHeight: 260, overflowY: "auto",
              position: "relative", marginBottom: 16, color: "#111"
            }}>
              <strong>Çalışma Planın:</strong>
              <div style={{ margin: "16px 0", whiteSpace: "pre-line" }}>{plan}</div>
              <button onClick={handleDeletePlan} style={{
                position: "absolute", top: 14, right: 14, border: "none", background: "#ef4444",
                color: "#fff", borderRadius: 6, padding: "4px 10px", cursor: "pointer", fontWeight: "bold"
              }}>
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
          padding: 12,
          marginTop: 12,
          width: "100%",  // 🔥 tam hizalandık
          height: 460,
          overflow: "hidden",
          textAlign: "center"
        }}>
          <div style={{
            fontWeight: "bold",
            fontSize: 16,
            marginBottom: 10,
            color: "#fff",
            backgroundColor: "#2563eb",
            borderRadius: 8,
            padding: "6px 0"
          }}>
            📌 Etkinlikler
          </div>

          {events.length === 0 ? (
            <div style={{ fontStyle: "italic", color: "#888" }}>Etkinlik bulunamadı.</div>
          ) : (
            events.slice(0, 3).map(event => (
              <div key={event.url} style={{
                backgroundColor: "#f9fafb",
                borderRadius: 8,
                marginBottom: 10,
                boxShadow: "0 1px 4px rgba(0,0,0,0.1)",
                overflow: "hidden",
                height: 130,
                width: "100%",
                margin: "0 auto"
              }}>
                <div style={{ width: "100%", height: 60, overflow: "hidden" }}>
                  <img
                    src={event.image || 'https://via.placeholder.com/300x200?text=Gorsel+Yok'}
                    alt="Etkinlik Görseli"
                    style={{ width: "100%", height: "100%", objectFit: "cover" }}
                    onError={(e) => e.target.src = 'https://via.placeholder.com/300x200?text=Gorsel+Yok'}
                  />
                </div>
                <div style={{ padding: 6 }}>
                  <div style={{
                    fontWeight: "bold",
                    fontSize: 13,
                    marginBottom: 4,
                    color: "#111",
                    whiteSpace: "nowrap",
                    overflow: "hidden",
                    textOverflow: "ellipsis"
                  }}>
                    {emojis[event.category]} {event.title}
                  </div>
                  <div style={{ fontSize: 11, color: "#555" }}>{event.city} - {event.start}</div>

                  <a href={event.url} target="_blank" rel="noopener noreferrer"
                    style={{
                      display: "inline-block",
                      marginTop: 4,
                      padding: "3px 8px",
                      background: "#2563eb",
                      color: "white",
                      textDecoration: "none",
                      borderRadius: 6,
                      fontWeight: "bold",
                      fontSize: 11
                    }}>
                    İncele
                  </a>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
