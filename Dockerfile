FROM python:3.9-slim

WORKDIR /src

COPY requirements.txt .

RUN apt-get update && apt-get install -y \
    libicu-dev \
    libpq-dev \
    gcc \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

VOLUME ["/uploads"]

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "5000", "--workers", "8"]