import React from "react"; 
import { useNavigate } from "react-router-dom";
function ResourceCard({ html, onStarClick, isFavorited }) {
  return (
    <div style={{
      border: "1px solid #ccc",
      borderRadius: 14,
      padding: 12,
      marginBottom: 10,
      background: "#fafafa",
      position: "relative"
    }}>
      <div
        style={{ position: "absolute", top: 10, right: 10, cursor: "pointer", fontSize: 20 }}
        onClick={onStarClick}
        title={isFavorited ? "Favorilerden çıkar" : "Favorilere ekle"}
      >
        {isFavorited ? "⭐" : "☆"}
      </div>
      <div dangerouslySetInnerHTML={{ __html: html }} />
    </div>
  );
}

const FavoritesPage = ({ favorites, setFavorites }) => {
  const navigate = useNavigate();

  return (
    <div style={{ padding: 24 }}>
      <button onClick={() => navigate(-1)} style={{ marginBottom: 16 }}>← Geri</button>
      <h2>⭐ Favorilerim</h2>
      {favorites.length === 0 && <p>Henüz hiç favorin yok!</p>}
      {favorites.map((fav, idx) => (
        <ResourceCard
          key={idx}
          html={fav}
          onStarClick={() => setFavorites(favorites.filter(f => f !== fav))}
          isFavorited={true}
        />
      ))}
    </div>
  );
};

export default FavoritesPage;
