import React, { useEffect, useState } from 'react';
import { jwtDecode } from 'jwt-decode';
import '../styles/Dashboard.css';
import Sidebar from '../components/Sidebar';
import logo from '../logo.svg';
import { useNavigate } from 'react-router-dom';

const Dashboard = () => {
  const [username, setUsername] = useState('');
  const [examSchedules, setExamSchedules] = useState([]);
  // 🔥 State tanımını buraya AL!
  const [newExam, setNewExam] = useState({
    course_name: '',
    exam_type: '',
    exam_date: '',
    exam_time: '',
  });

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

  // Sınav programlarını çek
  useEffect(() => {
    const token = localStorage.getItem('access');
    if (!token) return;
    fetch('http://localhost:8000/api/exam-schedules/', {
      headers: {
        'Authorization': `Bearer ${token}`,
      }
    })
    .then(res => res.json())
    .then(data => setExamSchedules(data))
    .catch(err => console.error('Sınav programı çekilemedi:', err));
  }, []);

  // Formdan yeni sınav ekleme
  const handleChange = (e) => {
    setNewExam({
      ...newExam,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const token = localStorage.getItem('access');
    fetch('http://localhost:8000/api/exam-schedules/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(newExam)
    })
    .then(async res => {
      if (res.ok) return res.json();
      const err = await res.json();
      throw new Error(JSON.stringify(err));
    })
    .then(data => {
      setExamSchedules([...examSchedules, data]);
      setNewExam({ course_name: '', exam_type: '', exam_date: '', exam_time: '' });
    })
    .catch(err => alert("Sınav eklenemedi: " + err.message));
  };

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
          <h2>Hoş geldin {username}!</h2>
        </div>

        <div className="chatbot-section">
          <div className="chatbot-card">Chatbot 1</div>
          <div className="chatbot-card">Chatbot 2</div>
          <div className="chatbot-card">Chatbot 3</div>
        </div>

        {/* Sınav Ekleme Formu */}
        <form onSubmit={handleSubmit} className="exam-form">
          <input
            type="text"
            name="course_name"
            placeholder="Ders Adı"
            value={newExam.course_name}
            onChange={handleChange}
            required
          />
          <input
            type="text"
            name="exam_type"
            placeholder="Sınav Türü (Vize/Final)"
            value={newExam.exam_type}
            onChange={handleChange}
            required
          />
          <input
            type="date"
            name="exam_date"
            value={newExam.exam_date}
            onChange={handleChange}
            required
          />
          <input
            type="time"
            name="exam_time"
            value={newExam.exam_time}
            onChange={handleChange}
            required
          />
          <button type="submit">Sınav Ekle</button>
        </form>

        {/* Gerçek Sınav Programı Tablosu */}
        <div className="schedule-section">
          <h3>Sınav Programı</h3>
          <table className="schedule-table">
            <thead>
              <tr>
                <th>Ders</th>
                <th>Sınav Türü</th>
                <th>Tarih</th>
                <th>Saat</th>
              </tr>
            </thead>
            <tbody>
              {examSchedules.map((exam, idx) => (
                <tr key={idx}>
                  <td>{exam.course_name}</td>
                  <td>{exam.exam_type}</td>
                  <td>{exam.exam_date}</td>
                  <td>{exam.exam_time}</td>
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
