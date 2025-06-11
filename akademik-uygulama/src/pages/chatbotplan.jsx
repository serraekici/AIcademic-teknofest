import React, { useState } from "react";

const studyMethods = [
  { value: "pomodoro", label: "Pomodoro (25 dk çalışma + 5 dk mola)" },
  { value: "blok", label: "Blok (Uzun süreli, odaklanmış seanslar)" },
  { value: "klasik", label: "Klasik (Derse göre gün ayırma)" },
  { value: "yoğun tekrar", label: "Yoğun Tekrar (Sınava yakın sık tekrar)" },
];

const ChatbotPlan = () => {
  const [selectedMethod, setSelectedMethod] = useState("pomodoro");
  const [customRequest, setCustomRequest] = useState("");
  const [planResult, setPlanResult] = useState('');
  const [isLoadingPlan, setIsLoadingPlan] = useState(false);

  // Planı oluşturma fonksiyonu
  const handlePlanRequest = async () => {
    setIsLoadingPlan(true);
    setPlanResult('');
    try {
      const jwt_token = localStorage.getItem('access');
      const res = await fetch('http://localhost:5000/api/generate-study-plan/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          study_method: selectedMethod,
          custom_request: customRequest,
          jwt_token: jwt_token,
        }),
      });
      const data = await res.json();
      if (data.plan) {
        setPlanResult(data.plan);
        localStorage.setItem("studyPlan", data.plan);
      } else {
        setPlanResult('Bir hata oluştu: ' + (data.error || 'Bilinmeyen hata'));
      }
    } catch (err) {
      setPlanResult('Bir hata oluştu: ' + err.message);
    }
    setIsLoadingPlan(false);
  };

  return (
  <div style={{
    maxWidth: 500,
    margin: "40px auto",
    background: "#fff",
    borderRadius: 16,
    boxShadow: "0 8px 32px rgba(0,0,0,0.12)",
    padding: 32,
    color: "#111" // <-- Buraya eklendi!
  }}>
    <h2>GPT Çalışma Planı Chatbotu</h2>
    <div style={{ marginBottom: 16 }}>
      <label>
        Çalışma Yöntemi Seç:
        <select
          style={{ marginLeft: 12, padding: 4, borderRadius: 6 }}
          value={selectedMethod}
          onChange={e => setSelectedMethod(e.target.value)}
        >
          {studyMethods.map(m => (
            <option key={m.value} value={m.value}>{m.label}</option>
          ))}
        </select>
      </label>
    </div>
    <div style={{ marginBottom: 16 }}>
      <label>
        Özel İsteklerin (ör. öncelikli ders, saat aralığı, mola tercihi, sınav tarihi vb):
        <textarea
          style={{
            width: "100%",
            height: 60,
            marginTop: 8,
            borderRadius: 6,
            padding: 8,
            border: "1px solid #ddd",
            color: "#111"  // <-- textarea için de ekledim!
          }}
          value={customRequest}
          onChange={e => setCustomRequest(e.target.value)}
          placeholder="Buraya isteklerini yazabilirsin..."
        />
      </label>
    </div>
    <button
      type="button"
      onClick={handlePlanRequest}
      disabled={isLoadingPlan}
      style={{
        padding: "8px 18px",
        borderRadius: 8,
        border: "none",
        background: "#2940d3",
        color: "#fff",
        fontWeight: "bold",
        cursor: "pointer"
      }}
    >
      {isLoadingPlan ? "Oluşturuluyor..." : "Plan Oluştur"}
    </button>
    <div style={{ whiteSpace: "pre-line", minHeight: 100, marginTop: 24 }}>
      {planResult && (
        <div>
          <strong>Çalışma Planı:</strong>
          <br />
          {planResult}
        </div>
      )}
    </div>
  </div>
);
};

export default ChatbotPlan;
