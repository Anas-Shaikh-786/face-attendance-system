# 🎯 Face Attendance System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![InsightFace](https://img.shields.io/badge/InsightFace-buffalo__sc-blueviolet?style=for-the-badge)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![GCP](https://img.shields.io/badge/Google_Cloud-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)

A real-time face recognition based attendance system built with InsightFace, Redis, and Streamlit — deployed on Google Cloud Run.

**🔴 Live Demo:** `https://face-attendance-system-enspuvmucpstfvmw63m8qb.streamlit.app/`

</div>

---

## 📸 Features

- **Real-Time Face Recognition** — detects and identifies faces live via webcam using InsightFace
- **Attendance Logging** — automatically logs name, role, and timestamp to Redis every 30 seconds
- **Face Registration** — register new users by capturing face embeddings through webcam
- **Attendance Reports** — view and download attendance logs as CSV
- **Cloud Deployment** — fully containerized with Docker, deployed on GCP Cloud Run

---

## 🏗️ Architecture

```
User (Webcam) 
    │
    ▼
Streamlit WebRTC  ──►  InsightFace (buffalo_sc)
                              │
                              ▼
                     Cosine Similarity Search
                              │
                              ▼
                     Redis (RedisLabs Cloud)
                      ├── academy:register   (face embeddings)
                      └── attendance:logs    (attendance records)
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit, streamlit-webrtc |
| Face Detection & Recognition | InsightFace (buffalo_sc), ONNX Runtime |
| Similarity Search | Scikit-learn Cosine Similarity |
| Database | Redis (RedisLabs Cloud) |
| Computer Vision | OpenCV |
| Containerization | Docker |
| Deployment | shre.streamlit.io |

---

## 📁 Project Structure

```
face_attendance_gcp/
├── Home.py                        # Main entry point
├── face_rec.py                    # Core face recognition logic
├── requirements.txt
├── Dockerfile
├── .streamlit/
│   └── config.toml                # Streamlit server config
└── pages/
    ├── 1_Real_time_prediction.py  # Live face recognition + logging
    ├── 2_Registration_form.py     # Register new users
    └── 3_Report.py                # View & download attendance logs
```

---

## ⚙️ How It Works

**Registration**
1. User enters name and role
2. Webcam captures face frames
3. InsightFace extracts 512-dimensional face embeddings
4. Mean embedding saved to Redis under `academy:register`

**Real-Time Prediction**
1. Webcam stream processed frame by frame
2. InsightFace detects faces and extracts embeddings
3. Cosine similarity compared against all registered embeddings
4. Match found if similarity ≥ 0.5 threshold
5. Attendance logged to Redis every 30 seconds

---

## 🚀 Local Setup

### Prerequisites
- Python 3.10+
- Redis account (RedisLabs free tier works)
- Webcam

### Steps

```bash
# Clone the repo
git clone https://github.com/Anas-Shaikh-786/face-attendance-system.git
cd face-attendance-system

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows Git Bash
# or
source venv/bin/activate       # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Fill in your Redis credentials in .env

# Run the app
streamlit run Home.py
```

### Environment Variables

Create a `.env` file in the root directory:

```env
REDIS_HOST=your-redis-host
REDIS_PORT=your-redis-port
REDIS_PASSWORD=your-redis-password
```

---

## 🐳 Docker

```bash
# Build
docker build -t face-attendance-app .

# Run
docker run -p 8501:8501 \
  -e REDIS_HOST=your-host \
  -e REDIS_PORT=your-port \
  -e REDIS_PASSWORD=your-password \
  face-attendance-app
```

---

## ☁️ GCP Cloud Run Deployment

```bash
# Build and push to GCR
docker build -t gcr.io/YOUR_PROJECT_ID/attendance-app .
gcloud auth configure-docker
docker push gcr.io/YOUR_PROJECT_ID/attendance-app

# Deploy
gcloud run deploy attendance-app \
  --image gcr.io/YOUR_PROJECT_ID/attendance-app \
  --platform managed \
  --region asia-south1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --port 8501 \
  --set-env-vars REDIS_HOST="...",REDIS_PORT="...",REDIS_PASSWORD="..."
```

---

## 👤 Author

**Shaikh Mohammed Anas **  
BCA Graduate | Aspiring Data Scientist & ML Engineer  
[![GitHub](https://img.shields.io/badge/GitHub-Anas--Shaikh--786-181717?style=flat&logo=github)](https://github.com/Anas-Shaikh-786)
