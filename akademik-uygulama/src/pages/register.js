import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/style.css';

const Register = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [password2, setPassword2] = useState('');
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch("http://127.0.0.1:8000/api/register/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          username: username,
          email: email,
          password: password,
          password2: password2
        })
      });

      const result = await response.json();

      if (response.ok) {
        setMessage("Kayıt başarılı! Giriş sayfasına yönlendiriliyorsunuz...");
        setTimeout(() => navigate("/login"), 2000);
      } else {
        setMessage("Kayıt başarısız: " + (result.detail || JSON.stringify(result)));
      }
    } catch (error) {
      setMessage("Bağlantı hatası: Sunucuya ulaşılamıyor.");
      console.error("Kayıt hatası:", error);
    }
  };

  return (
    <div className="container">
      <div className="left">
        <h2>Araştır, Öğren, Çalışmaya Başla!</h2>
        <p>Sana özel çalışma programına göz at!</p>
        <img src="/study.svg" alt="Study Illustration" className="study-image" />
        <p className="caption">Ders kaynaklarını incele!</p>
      </div>

      <div className="right">
        <h2>Kayıt Ol</h2>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="İsminiz ve Soyisminiz"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <input
            type="email"
            placeholder="E-Posta"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Şifre Oluşturun"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Şifrenizi Onaylayın"
            value={password2}
            onChange={(e) => setPassword2(e.target.value)}
            required
          />
          <button type="submit">Hemen Başla!</button>
        </form>

        <div id="response-message" style={{ marginTop: "10px", color: "red" }}>
          {message}
        </div>
        <h2>Zaten hesabın var mı?</h2>
        <p className="note">Hemen giriş yap!</p>
        <button className="main-button" onClick={() => navigate("/login")}>Giriş Yap</button>
      </div>
    </div>
  );
};

export default Register;
