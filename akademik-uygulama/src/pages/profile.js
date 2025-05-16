import React from 'react';
import '../styles/style.css'; // Eğer ortak stiller kullanıyorsan

const Profile = () => {
  const username = localStorage.getItem('username') || 'Kullanıcı';

  return (
    <div className="container">
      <div className="profile-card">
        <h2>Profil Sayfası</h2>
        <p><strong>Kullanıcı Adı:</strong> {username}</p>
        <p>Bu sayfa, kullanıcının bilgilerini ve özelleştirilmiş içerikleri göstermek için kullanılabilir.</p>
      </div>
    </div>
  );
};

export default Profile;
