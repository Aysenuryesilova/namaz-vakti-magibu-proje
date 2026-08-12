# ==============================================================================
# İSLÂMİ DENETÇİ ASİSTAN - DOCKER İMAJ DOSYASI (DOCKERFILE)
# ==============================================================================
# Bu dosya, uygulamanın çalışması için gerekli tüm Python ortamını, bağımlılıkları
# ve Gradio Web UI portunu (7860) konteynerize eder.
# ==============================================================================

# 1. Taban İmaj (Official Python 3.11 Slim Image)
FROM python:3.11-slim

# 2. Çalışma Dizini Oluşturma
WORKDIR /app

# 3. Sistem Bağımlılıkları Kurulumu
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 4. Python Paket Bağımlılıklarını Kopyalama ve Kurma
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Proje Kodlarını Kopyalama
COPY . .

# 6. Gradio Web UI Portunu Dışa Açma
EXPOSE 7860

# 7. Varsayılan Başlatma Komutu (Gradio Web UI)
CMD ["python", "app.py"]
