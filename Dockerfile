FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    ffmpeg chromium chromium-driver xvfb \
    libatk-bridge2.0-0 libgtk-3-0 libnss3 \
    libxcomposite1 libxdamage1 libxrandr2 \
    libgbm1 libasound2 libdrm2 libxshmfence1 \
    && rm -rf /var/lib/apt/lists/*

ENV DISPLAY=:99
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["bash","-lc","xvfb-run -a python main.py"]
