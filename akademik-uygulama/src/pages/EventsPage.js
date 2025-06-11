import React, { useEffect, useState } from "react";

function EventsPage() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("http://localhost:8000/api/ticketmaster-events/")
      .then((res) => {
        if (!res.ok) throw new Error("API Hatası");
        return res.json();
      })
      .then((data) => {
        setEvents(data);
        setLoading(false);
      })
      .catch((err) => {
        setError("Veri alınamadı: " + err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Yükleniyor...</div>;
  if (error) return <div style={{ color: "red" }}>{error}</div>;

  // Emoji eşlemesi
  const emojis = {
    "Konser": "🎵",
    "Tiyatro": "🎭",
    "Festival": "🎉",
    "Sergi": "🖼️",
    "Workshop": "🛠️",
    "Genel": "📌"
  };

  return (
    <div style={{ padding: 40, textAlign: "center" }}>
      <h1>🎭 Güncel Etkinlikler (5 Kategori)</h1>
      <div style={{
        display: "flex", flexWrap: "wrap", justifyContent: "center", gap: 30
      }}>
        {events.map(event => (
          <div key={event.url} style={{
            background: "white",
            borderRadius: 12,
            boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
            width: 300,
            overflow: "hidden",
            textAlign: "left"
          }}>
            <img
              src={event.image}
              alt="Etkinlik Görseli"
              style={{ width: "100%", height: 200, objectFit: "cover" }}
              onError={e => e.target.src = 'https://via.placeholder.com/300x200?text=Gorsel+Yok'}
            />
            <div style={{ padding: 15 }}>
              <h3 style={{ margin: "0 0 10px 0", fontSize: 18, color: "#007BFF" }}>
                {emojis[event.category] || ""} {event.category} – {event.title}
              </h3>
              <p><strong>Tarih:</strong> {event.start}</p>
              <p><strong>Şehir:</strong> {event.city}</p>
              <a
                href={event.url}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: "inline-block",
                  marginTop: 10,
                  padding: 10,
                  background: "#007BFF",
                  color: "white",
                  textDecoration: "none",
                  borderRadius: 5
                }}
              >
                Etkinliğe Git
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default EventsPage;
