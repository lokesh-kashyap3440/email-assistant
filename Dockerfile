FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends nodejs npm && rm -rf /var/lib/apt/lists/*

COPY frontend/package.json frontend/package-lock.json* ./frontend/
RUN cd frontend && npm install
COPY frontend/ ./frontend/
RUN cd frontend && npm run build

COPY server/requirements.txt ./server/
RUN pip install --no-cache-dir -r server/requirements.txt

COPY pyproject.toml .
COPY email_assistant/ ./email_assistant/
RUN pip install -e .

COPY server/ ./server/

EXPOSE 7860
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "7860"]
