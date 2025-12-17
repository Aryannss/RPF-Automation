FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY app/requirements.txt /app/requirements.txt

RUN pip install --upgrade pip
RUN pip install --no-cache-dir fastapi uvicorn[standard] python-multipart pydantic numpy pandas python-dotenv pdfminer.six reportlab aiofiles
RUN pip install --no-cache-dir sentence-transformers==2.2.2 --no-deps

COPY app /app/app

ENV PYTHONPATH=/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
