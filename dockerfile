FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libffi-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN pip install -r requirements.txt
RUN pip install -r requirements_dev.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
