import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/style.css';
import { jwtDecode } from 'jwt-decode';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("access");
    if (token) {
      navigate("/dashboard");
    }
  }, [navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch("http://127.0.0.1:8000/api/token/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ username, password })
      });

      const result = await response.json();

      if (response.ok) {
        localStorage.setItem("access", result.access);
        localStorage.setItem("refresh", result.refresh);

        const decoded = jwtDecode(result.access);
        if (decoded?.username) {
          localStorage.setItem("username", decoded.username);
        }

        navigate("/dashboard");
      } else {
        setMessage("Hatalı kullanıcı adı veya şifre.");
      }
    } catch (error) {
      console.error("Giriş hatası:", error);
      setMessage("Sunucuya ulaşılamadı.");
    }
  };

  const handleSignup = () => {
    navigate("/register");
  };

  return (
    <div
      className="container"
      style={{
        background: "linear-gradient(to right, #f3e5f5, #e3f2fd)",
        borderRadius: 30,
        boxShadow: "0 0 12px rgba(0,0,0,0.05)",
        padding: 40,
        marginTop: 40,
      }}
    >
      <div className="left">
        <h2 style={{ color: "#6a1b9a" }}>Araştır, Öğren, Çalışmaya Başla!</h2>
        <p style={{ color: "#4a148c" }}>Sana özel çalışma programına göz at!</p>
        <img src="loog.jpg" alt="Study" className="study-image" />
        <p className="caption">Ders kaynaklarını incele!</p>
      </div>

      <div className="right">
        <h2 style={{ color: "#4a148c" }}>Giriş Yap</h2>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Kullanıcı Adı"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            style={{
              border: "1px solid #ce93d8",
              backgroundColor: "#fffff",
              color: "#4a148c"
            }}
          />
          <input
            type="password"
            placeholder="Şifre"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{
              border: "1px solid #ce93d8",
              backgroundColor: "#fffff",
              color: "#4a148c"
            }}
          />
          <button
            type="submit"
            style={{
              backgroundColor: "#6a1b9a",
              color: "#fff",
              borderRadius: 20,
              fontWeight: "bold"
            }}
          >
            Giriş Yap
          </button>
        </form>

        {message && (
          <div id="response-message" style={{ marginTop: 10, color: "red" }}>
            {message}
          </div>
        )}

        <h2 style={{ marginTop: 30, color: "#6a1b9a" }}>Ücretsiz Kayıt Ol</h2>
        <p className="note">Öğrenci e-postanla kayıt olarak Premium özellikleri keşfet!</p>

        <button
          onClick={handleSignup}
          className="main-button"
          style={{
            backgroundColor: "#6a1b9a",
            color: "#fff",
            borderRadius: 20,
            marginTop: 10,
            fontWeight: "bold"
          }}
        >
          Kayıt Ol
        </button>
      </div>
    </div>
  );
};

export default Login;
