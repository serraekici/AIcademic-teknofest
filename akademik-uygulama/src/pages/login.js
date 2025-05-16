import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/style.css'; // varsa CSS bağlantını yap

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

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
        localStorage.setItem("username", username);  // 🔥 Burada kullanıcı adını saklıyoruz

        setMessage("Giriş başarılı!");
        setTimeout(() => navigate("/"), 1500); // Anasayfaya yönlendir
      } else {
        setMessage("Hatalı giriş bilgileri: " + JSON.stringify(result));
      }
    } catch (error) {
      setMessage("Sunucuya bağlanılamıyor.");
      console.error(error);
    }
  };

  const handleSignup = () => {
    navigate("/register"); // kayıt sayfan varsa yönlendir
  };

  return (
    <div className="container">
      <div className="left">
        <h2>Araştır, Öğren, Çalışmaya Başla!</h2>
        <p>Sana özel çalışma programına göz at!</p>
        <img src="study.svg" alt="Study Illustration" className="study-image" />
        <p className="caption">Ders kaynaklarını incele!</p>
      </div>

      <div className="right">
        <h2>Giriş Yap</h2>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button type="submit">Giriş Yap</button>
        </form>

        <div id="response-message" style={{ marginTop: "10px", color: "red" }}>{message}</div>

        <h2>Ücretsiz Kayıt ol ve Hemen Çalışmaya Başla!</h2>
        <p className="note">Öğrenci e-postanla kayıt olarak Premium özelliklerini keşfet!</p>

        <button onClick={handleSignup} className="main-button">Kayıt Ol!</button>
      </div>
    </div>
  );
};

export default Login;
