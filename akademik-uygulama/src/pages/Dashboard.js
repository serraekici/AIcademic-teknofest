import React from 'react';
import '../styles/Dashboard.css';
import Sidebar from '../components/Sidebar';
import logo from '../logo.svg';

const Dashboard = () => {
  return (
    <div className="dashboard-container">
      <Sidebar />

      <div className="main-content">
        <div className="logo-section">
          <img src={logo} alt="Logo" className="main-logo" />
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
