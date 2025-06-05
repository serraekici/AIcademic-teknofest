import React, { useState } from "react";

const studyMethods = [
  { value: "pomodoro", label: "Pomodoro (25 dk çalışma + 5 dk mola)" },
  { value: "blok", label: "Blok (Uzun süreli, odaklanmış seanslar)" },
  { value: "klasik", label: "Klasik (Derse göre gün ayırma)" },
  { value: "yoğun tekrar", label: "Yoğun Tekrar (Sınava yakın sık tekrar)" },
];

const ChatbotPlan = () => {
  const [selectedMethod, setSelectedMethod] = useState("pomodoro");
  const [planResult, setPlanResult] = useState('');
  const [isLoadingPlan, setIsLoadingPlan] = useState(false);

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
          jwt_token: jwt_token,
        }),
      });
      const data = await res.json();
      if (data.plan) {
        setPlanResult(data.plan);
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
    }}>
      <h2>GPT Çalışma Planı Chatbotu</h2>
      <div style={{ marginBottom: 24 }}>
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
        <button
          onClick={handlePlanRequest}
          disabled={isLoadingPlan}
          style={{
            marginLeft: 16,
            padding: "6px 16px",
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
      </div>
      <div style={{whiteSpace: "pre-line", minHeight: 100}}>
        {planResult && <div><strong>Çalışma Planı:</strong><br />{planResult}</div>}
      </div>
    </div>
  );
};

export default ChatbotPlan;
