:root {
  --bg: #0b1220;
  --panel: #121d2a;
  --panel-alt: #162637;
  --primary: #4cc9f0;
  --accent: #86efac;
  --warning: #f6c453;
  --danger: #ff7b72;
  --text: #ebf3ff;
  --muted: #b0c4d9;
  --border: rgba(255, 255, 255, 0.08);
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  background: linear-gradient(135deg, #07111d, #0e1c2d 60%, #0b1220);
  color: var(--text);
  font-family: Inter, "Segoe UI", sans-serif;
}

.page-shell {
  max-width: 1220px;
  margin: 0 auto;
  padding: 32px 20px 50px;
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.eyebrow {
  margin: 0 0 10px;
  color: var(--primary);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 12px;
}

h1, h2, h3, p {
  margin-top: 0;
}

h1 {
  margin-bottom: 0;
  font-size: clamp(2rem, 4vw, 3rem);
}

.badge {
  background: rgba(76, 201, 240, 0.12);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 9px 16px;
  color: var(--primary);
  font-weight: 600;
}

.layout {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 20px;
}

.panel {
  background: rgba(18, 29, 42, 0.9);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 20px;
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.18);
}

.form-panel, .supplier-panel {
  min-height: 220px;
}

.result-panel {
  grid-column: 1 / -1;
}

.field-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(220px, 1fr));
  gap: 16px;
}

label {
  display: flex;
  flex-direction: column;
  gap: 8px;
  color: var(--muted);
  font-size: 14px;
}

input {
  width: 100%;
  background: rgba(10, 17, 28, 0.9);
  border: 1px solid var(--border);
  border-radius: 10px;
  color: var(--text);
  padding: 12px 14px;
  font-size: 15px;
}

button {
  margin-top: 18px;
  border: none;
  border-radius: 12px;
  padding: 12px 18px;
  background: linear-gradient(135deg, var(--primary), #5b8def);
  color: #07111d;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
}

.supplier-list {
  display: grid;
  gap: 14px;
}

.supplier-card {
  background: rgba(18, 37, 54, 0.8);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 14px 16px;
}

.supplier-card h3 {
  margin-bottom: 8px;
  font-size: 1.06rem;
}

.meta {
  color: var(--muted);
  font-size: 13px;
  line-height: 1.6;
}

.summary-box {
  padding: 18px 20px;
  border-radius: 12px;
  background: rgba(76, 201, 240, 0.09);
  border: 1px solid rgba(76, 201, 240, 0.25);
  color: var(--text);
  line-height: 1.6;
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
  margin-top: 18px;
}

.result-card {
  background: rgba(17, 30, 43, 0.8);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 18px;
}

.result-card h3 {
  margin-bottom: 14px;
}

.cost-line {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  padding: 6px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  color: var(--muted);
}

.cost-line strong {
  color: var(--text);
}

.badge-success {
  color: var(--accent);
  font-weight: 700;
}

.badge-warning {
  color: var(--warning);
  font-weight: 700;
}

@media (max-width: 820px) {
  .layout {
    grid-template-columns: 1fr;
  }

  .field-grid {
    grid-template-columns: 1fr;
  }

  .topbar {
    flex-direction: column;
    align-items: flex-start;
  }
}
