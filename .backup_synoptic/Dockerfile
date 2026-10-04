FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libeccodes-dev libeccodes-tools \
    libproj-dev proj-bin proj-data \
    libgeos-dev \
    libgdal-dev gdal-bin \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "-b", "0.0.0.0:8000", "server:app"]