import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Login from './pages/login'; 
import Register from './pages/register';
import Profile from './pages/profile';
import ChatbotPlan from './pages/chatbotplan';
import ExamSchedulePage from './pages/ExamSchedulePage';
import KaynakChatbot from "./pages/kaynakchatbot";
import FavoritesPage from './pages/FavoritesPage';
import EventsPage from "./pages/EventsPage";
// Korumalı rota: token yoksa login'e atıyor
const PrivateRoute = ({ children }) => {
  const token = localStorage.getItem("access");
  return token ? children : <Navigate to="/login" />;
};
  

const App = () => {
  const [favorites, setFavorites] = useState(() => {
    const saved = localStorage.getItem("favorites");
    return saved ? JSON.parse(saved) : [];
  });
    useEffect(() => {
    localStorage.setItem("favorites", JSON.stringify(favorites));
  }, [favorites]);

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        
        <Route
          path="/kaynakchatbot"
          element={
            <PrivateRoute>
              <KaynakChatbot
                favorites={favorites}
                setFavorites={setFavorites}
              />
            </PrivateRoute>
          }
        />
        <Route path="/events" 
        element={<EventsPage />} />
        <Route
          path="/dashboard"
          element={
            <PrivateRoute>
              <Dashboard />
            </PrivateRoute>
          }
        />
        <Route
          path="/exam-schedule"
          element={
            <PrivateRoute>
              <ExamSchedulePage />
            </PrivateRoute>
          }
        />
        <Route
          path="/chatbot-plan"
          element={
            <PrivateRoute>
              <ChatbotPlan />
            </PrivateRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <PrivateRoute>
              <Profile />
            </PrivateRoute>
          }
        />
        <Route
          path="/favorites"
          element={
            <PrivateRoute>
              <FavoritesPage
                favorites={favorites}
                setFavorites={setFavorites}
              />
            </PrivateRoute>
          }
        />
        <Route path="/" element={<Navigate to="/dashboard" />} />
      </Routes>
    </Router>
  );
};

export default App;
