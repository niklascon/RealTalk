# .devcontainer/Dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libssl-dev \
    libasound2-dev \
    libpulse-dev \
    libportaudio2 \
    portaudio19-dev \
    python3-tk \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
RUN useradd -m vscode
USER vscode

COPY backend/requirements.txt .
RUN pip install -r requirements.txt

ENV PATH=/home/vscode/.local/bin:$PATH




