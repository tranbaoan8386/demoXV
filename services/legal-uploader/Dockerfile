FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8083

# Install a minimal LibreOffice subset to enable .doc -> .docx conversion
# Avoid installing full 'libreoffice' or Java packages which can cause large installs
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    libreoffice-core \
    libreoffice-writer \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ /app/src/
COPY migrations/ /app/migrations/

# Ensure package import path includes /app
ENV PYTHONPATH=/app

EXPOSE 8083

CMD ["uvicorn", "src.presentation.api:app", "--host", "0.0.0.0", "--port", "8083"]
