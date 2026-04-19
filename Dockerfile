# ✅ Use slim Python base
FROM python:3.10-slim

# ✅ System dependencies for InsightFace + OpenCV + build tools
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgomp1 \
    cmake \
    build-essential \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ✅ Install Python dependencies first (Docker cache optimization)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Pre-download buffalo_l model at build time (avoids cold start delays)
RUN python -c "\
from insightface.app import FaceAnalysis; \
app = FaceAnalysis(name='buffalo_l', root='insightFace', providers=['CPUExecutionProvider']); \
app.prepare(ctx_id=0, det_size=(640,640)); \
print('buffalo_l model downloaded successfully')"

# ✅ Copy all app files
COPY . .

# ✅ Streamlit config to disable file watcher (important for containers)
RUN mkdir -p /root/.streamlit
COPY .streamlit/config.toml /root/.streamlit/config.toml

EXPOSE 8501

# ✅ Cloud Run uses PORT env variable — but Streamlit needs explicit port
CMD ["streamlit", "run", "Home.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
