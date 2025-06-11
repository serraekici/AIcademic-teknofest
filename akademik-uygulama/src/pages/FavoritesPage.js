import React from "react"; 
import { useNavigate } from "react-router-dom";
import "./FavoritesPage.css"; // CSS dosyasını import et

function ResourceCard({ html, onStarClick, isFavorited }) {
  return (
    <div className="resource-card">
      <button
        className={`star-btn${isFavorited ? " favorited" : ""}`}
        onClick={onStarClick}
        title={isFavorited ? "Favorilerden çıkar" : "Favorilere ekle"}
      >
        {isFavorited ? "★" : "☆"}
      </button>
      <div className="resource-content" dangerouslySetInnerHTML={{ __html: html }} />
    </div>
  );
}

const FavoritesPage = ({ favorites, setFavorites }) => {
  const navigate = useNavigate();

  return (
    <div className="favorites-page">
      <button className="back-btn" onClick={() => navigate(-1)}>
        ← Geri
      </button>
      <h2 className="favorites-title">⭐ Favorilerim</h2>
      {favorites.length === 0 && (
        <p className="no-favorites">Henüz hiç favorin yok!</p>
      )}
      <div className="favorites-list">
        {favorites.map((fav, idx) => (
          <ResourceCard
            key={idx}
            html={fav}
            onStarClick={() => setFavorites(favorites.filter(f => f !== fav))}
            isFavorited={true}
          />
        ))}
      </div>
    </div>
  );
};

export default FavoritesPage;
