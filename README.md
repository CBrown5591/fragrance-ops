# Fragrance Ops Command Center 🧴✨

A streamlined Streamlit web application powering the daily fragrance operations and layering matrix engine. Built directly on top of your **Google Drive Fragrance Matrix** spreadsheet, live weather telemetry (Open-Meteo), and sartorial color coordination.

---

## 🚀 Features

- **Live Google Sheets Integration**: Connects via Service Account to your live `Fragrance Matrix` in Google Drive with configurable caching.
- **Dynamic Weather & Seasonal Bracketing**: Pulls live temperature & humidity for Washington, D.C. (or any travel destination) and matches to your 6 seasonal bands:
  - Deep Winter (< 45°F)
  - Pre-Spring (Transitional 45°F – 58°F)
  - Spring (Warming 55°F – 70°F)
  - High Summer (75°F – 95°F+)
  - Early Fall (Transitional 58°F – 72°F)
  - Fall (Crisp 45°F – 60°F)
- **Daily Executive Briefing**: Automatically assigns an office-safe pairing (WP, EC, or intimate DN) respecting the $\le$ 4–5 ft sillage boundary, determines the Grooming Canvas (Unscented Body Butter < 65°F vs. Unscented Lotion $\ge$ 65°F), and renders sartorial color swatches.
- **Matrix Explorer & Idea Generator**:
  - Filter by Season, Scenario badges (`WP`, `EC`, `DN`, `LO`, `NL`), and Particle Primer compatibility.
  - "Surprise Me / Roll Idea" generator with built-in boundary clash guardrails.
- **Fragrance Directory & Search**: Look up individual standalone colognes, notes, and DNA references.

---

## 🛠️ Setup Instructions

### 1. Google Cloud Service Account Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/) and create a project.
2. Enable both **Google Sheets API** and **Google Drive API**.
3. Create a **Service Account** under **IAM & Admin > Service Accounts**, generate a JSON key, and download it.
4. Share your **Fragrance Matrix** Google Sheet with the client email found in your service account JSON (as *Viewer* or *Editor*).

### 2. Configure Streamlit Secrets (`.streamlit/secrets.toml`)
Create a `.streamlit/secrets.toml` file in the project root:

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project-id.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs/your-service-account"

spreadsheet_name = "Fragrance Matrix"
```

### 3. Local Run
```bash
git clone https://github.com/your-username/fragrance-ops.git
cd fragrance-ops
pip install -r requirements.txt
streamlit run app.py
```
