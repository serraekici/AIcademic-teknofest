import React, { useEffect, useState } from 'react';
import './ExamSchedulePage.css';

const ExamSchedulePage = () => {
  const [examSchedules, setExamSchedules] = useState([]);
  const [newExam, setNewExam] = useState({
    course_name: '',
    exam_type: '',
    exam_date: '',
    exam_time: '',
    difficulty: 'orta',
  });

  useEffect(() => {
    const token = localStorage.getItem('access');
    if (!token) return;
    fetch('http://localhost:8000/api/exam-schedules/', {
      headers: {
        'Authorization': `Bearer ${token}`,
      }
    })
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data.results)) {
          setExamSchedules(data.results);
        } else if (Array.isArray(data)) {
          setExamSchedules(data);
        } else {
          setExamSchedules([]);
        }
      })
      .catch(err => {
        console.error('Sınav programı çekilemedi:', err);
        setExamSchedules([]);
      });
  }, []);

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
        setExamSchedules(prev => [...prev, data]);
        setNewExam({ course_name: '', exam_type: '', exam_date: '', exam_time: '', difficulty: 'orta' });
      })
      .catch(err => alert("Sınav eklenemedi: " + err.message));
  };

  // --- Silme Fonksiyonu ---
  const handleDeleteExam = (examId) => {
    const token = localStorage.getItem('access');
    fetch(`http://localhost:8000/api/exam-schedules/${examId}/`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
      }
    })
      .then(res => {
        if (res.ok) {
          setExamSchedules(prev => prev.filter(exam => exam.id !== examId));
        } else {
          alert("Sınav silinemedi!");
        }
      });
  };

  return (
    <div className="exam-schedule-page">
      <h2>Sınav Takvimi</h2>
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
        <label htmlFor="difficulty" style={{ marginTop: "10px" }}>
          Senin için zorluk seviyesi:
        </label>
        <select
          id="difficulty"
          name="difficulty"
          value={newExam.difficulty}
          onChange={handleChange}
          required
        >
          <option value="kolay">Kolay</option>
          <option value="orta">Orta</option>
          <option value="zor">Zor</option>
        </select>
        <button type="submit">Sınav Ekle</button>
      </form>

      {/* Sınav Tablosu */}
      <div className="schedule-section">
        <h3>Sınav Programı</h3>
        <table className="schedule-table">
          <thead>
            <tr>
              <th>Ders</th>
              <th>Sınav Türü</th>
              <th>Tarih</th>
              <th>Saat</th>
              <th>Senin için zorluk seviyesi</th>
              <th>İşlem</th>
            </tr>
          </thead>
          <tbody>
            {Array.isArray(examSchedules) && examSchedules.map((exam, idx) => (
              <tr key={exam.id || idx}>
                <td>{exam.course_name}</td>
                <td>{exam.exam_type}</td>
                <td>{exam.exam_date}</td>
                <td>{exam.exam_time}</td>
                <td>{exam.difficulty || 'Belirtilmemiş'}</td>
                <td>
                  <button onClick={() => handleDeleteExam(exam.id)}>
                    Sil
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ExamSchedulePage;
