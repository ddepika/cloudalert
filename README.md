```markdown
# CloudAlert - Cloudburst Prediction System

A real-time cloudburst prediction system for Uttarakhand, Himachal Pradesh, and Jammu & Kashmir using Machine Learning.

## Features

- **Real-time Weather Monitoring**: Live weather data from OpenWeatherMap API for 20+ districts
- **ML-based Cloudburst Prediction**: GRU/LSTM model with 94.8% accuracy
- **Interactive Live Map**: OpenStreetMap integration showing district locations
- **Email Alerts**: Automated weather reports and risk notifications
- **User Authentication**: Secure login/signup with email verification
- **Historical Data**: IMD rainfall data analysis (2023-2025)
- **MOSDAC Integration**: ISRO satellite alert structure

## Covered Regions

### Uttarakhand (5 districts)
Uttarkashi, Chamoli, Rudraprayag, Bageshwar, Pithoragarh

### Himachal Pradesh (7 districts)
Mandi, Shimla, Chamba, Kullu, Sirmaur, Kangra, Kinnaur

### Jammu & Kashmir (8 districts)
Anantnag, Kulgam, Ganderbal, Kishtwar, Doda, Ramban, Reasi, Udhampur

## Tech Stack

### Backend
- FastAPI (Python)
- SQLAlchemy (Database)
- TensorFlow/Keras (ML Model)
- JWT Authentication
- SMTP Email Service

### Frontend
- React.js
- Material-UI
- Leaflet Maps
- Axios
- Recharts

### Data Sources
- OpenWeatherMap API
- IMD Gridded Rainfall Data
- MOSDAC/ISRO NETRA
- ERA5 Reanalysis (planned)

## Prerequisites

- Python 3.10+
- Node.js 18+
- OpenWeatherMap API key
- Gmail account (for email alerts)

## Installation

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## Model Performance

| Metric | Value |
|--------|-------|
| Accuracy | 94.8% |
| Precision | 93.3% |
| Recall | 87.5% |
| F1-Score | 90.3% |
| AUC-ROC | 98.2% |

## Project Structure

```
CloudBurst/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── models/       # Database models
│   │   ├── services/     # Business logic
│   │   └── utils/        # Utilities
│   ├── data/             # IMD and weather data
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   └── context/      # Auth context
│   └── package.json
└── README.md
```

## Environment Variables

Create `.env` file in backend directory:

```env
OPENWEATHER_API_KEY=your_api_key
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
DATABASE_URL=sqlite:///./cloudburst.db
```

## License

MIT License

## Author

**Deepika Rawat** - B.Tech CSE Final Year Project

---

*This project is for academic purposes. Always follow official disaster management guidelines.*
```
