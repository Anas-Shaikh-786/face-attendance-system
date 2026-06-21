# ✅ Use slim Python base
FROM python:3.10-slim

# ✅ Fix apt reliability issues
RUN rm -f /etc/apt/apt.conf.d/docker-clean \
    && echo 'Acquire::Retries "3";' > /etc/apt/apt.conf.d/80-retries \
    && echo 'Acquire::http::Timeout "120";' >> /etc/apt/apt.conf.d/80-retries

# ✅ System dependencies for InsightFace + OpenCV
RUN apt-get update --fix-missing && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    cmake \
    build-essential \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ✅ Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Pre-download buffalo_sc model at build time
RUN python -c "\
from insightface.app import FaceAnalysis; \
app = FaceAnalysis(name='buffalo_sc', root='insightFace', providers=['CPUExecutionProvider']); \
app.prepare(ctx_id=0, det_size=(640,640)); \
print('buffalo_sc model downloaded successfully')"

# ✅ Copy all app files
COPY . .

# ✅ Streamlit config
RUN mkdir -p /root/.streamlit
COPY .streamlit/config.toml /root/.streamlit/config.toml

EXPOSE 8501

CMD ["streamlit", "run", "Home.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
