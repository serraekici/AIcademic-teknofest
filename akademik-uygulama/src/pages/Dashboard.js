import React, { useEffect, useState } from 'react';
import Calendar from 'react-calendar';
import 'react-calendar/dist/Calendar.css';
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
    fetch("http://localhost:8000/api/local-events/")  // kendi API adresine göre ayarla
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
    <div className="dashboard-container" style={{ display: "flex" }}>
      <Sidebar />

      <div className="main-content" style={{ flex: 2, padding: 20 }}>
        <div className="logo-section" style={{ textAlign: "center", marginBottom: 20 }}>
          <img src={logo} alt="Logo" className="main-logo" style={{ width: 120 }} />
          <h2>Hoş geldin {username}!</h2>
        </div>

        {/* Chatbot Flip Kartları */}
        <div className="chatbot-section" style={{ display: "flex", gap: 16, marginBottom: 20 }}>
          <FlipCard
            front="GPT Çalışma Planı Chatbotu"
            back="Günlük çalışma planlarını yapay zekayla oluştur!"
            onClick={() => navigate("/chatbot-plan")}
          />
          <FlipCard
            front="Kaynak Chatbot"
            back="Ders kaynakları, kitap ve makale önerileri!"
            onClick={() => navigate("/kaynakchatbot")}
          />
          <FlipCard
            front="Tercih Chatbotu"
            back="Üniversite tercihlerini akıllı sistemle yap!"
            onClick={() => navigate("/tercihchatbot")}
          />
        </div>

        <div style={{ margin: "10px 0 8px 0" }}>
          {plan ? (
            <div style={planCardStyle}>
              <strong>Çalışma Planın:</strong>
              <div style={{ margin: "16px 0", whiteSpace: "pre-line" }}>{plan}</div>
              <button onClick={handleDeletePlan} style={deleteBtnStyle}>Sil</button>
            </div>
          ) : (
            <div style={{ color: "#555", fontStyle: "italic" }}>Henüz bir çalışma planı yok.</div>
          )}
        </div>
      </div>

      <div className="right-section" style={{ flex: 1, padding: 20 }}>
        {/* Takvim */}
        <div style={boxStyle}>
          <div style={boxTitleStyle}>📅 Takvim</div>
          <div style={{ display: "flex", justifyContent: "center" }}>
            <Calendar />
          </div>
        </div>

        {/* Etkinlikler */}
        <div style={{ ...boxStyle, marginTop: 20 }}>
          <div style={boxTitleStyle}>📌 Etkinlikler</div>

          {events.length === 0 ? (
            <div style={{ fontStyle: "italic", color: "#888" }}>Etkinlik bulunamadı.</div>
          ) : (
            events.slice(0, 3).map(event => (
              <div key={event.url} style={eventCardStyle}>
                <div style={imageContainerStyle}>
                  <img
                    src={event.image || 'https://via.placeholder.com/80x80?text=Görsel+Yok'}
                    alt="Etkinlik Görseli"
                    style={{ width: "100%", height: "100%", objectFit: "cover" }}
                    onError={(e) => e.target.src = 'https://via.placeholder.com/80x80?text=Görsel+Yok'}
                  />
                </div>

                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: "bold", fontSize: 13, marginBottom: 4, color: "#111" }}>
                    {emojis[event.category]} {event.title}
                  </div>
                  <div style={{ fontSize: 11, color: "#555", marginBottom: 6 }}>
                    {event.city} - {event.start}
                  </div>

                  <a href={event.url} target="_blank" rel="noopener noreferrer"
                    style={inceleBtnStyle}>
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

// Flip Card Bileşeni
const FlipCard = ({ front, back, onClick }) => (
  <div className="flip-card" onClick={onClick}>
    <div className="flip-card-inner">
      <div className="flip-card-front">{front}</div>
      <div className="flip-card-back">{back}</div>
    </div>
  </div>
);

// Stil Sabitleri
const planCardStyle = {
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
};

const deleteBtnStyle = {
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
};

const boxStyle = {
  background: "#fff",
  borderRadius: 12,
  boxShadow: "0 2px 8px rgba(0,0,0,0.07)",
  padding: 16,
  textAlign: "center"
};

const boxTitleStyle = {
  fontWeight: "bold",
  fontSize: 17,
  marginBottom: 10
};

const eventCardStyle = {
  display: "flex",
  alignItems: "center",
  backgroundColor: "#f9fafb",
  borderRadius: 8,
  marginBottom: 10,
  boxShadow: "0 1px 4px rgba(0,0,0,0.1)",
  overflow: "hidden",
  padding: 8
};

const imageContainerStyle = {
  width: 80,
  height: 80,
  flexShrink: 0,
  borderRadius: 8,
  overflow: "hidden",
  marginRight: 12
};

const inceleBtnStyle = {
  padding: "4px 10px",
  background: "#2563eb",
  color: "white",
  textDecoration: "none",
  borderRadius: 6,
  fontWeight: "bold",
  fontSize: 11
};

export default Dashboard;
