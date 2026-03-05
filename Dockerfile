FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

RUN groupadd --system appgroup && useradd --system --gid appgroup appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

CMD ["sh", "-c", "python scripts/init_db.py && gunicorn --bind 0.0.0.0:8000 --workers 2 --threads 4 --timeout 60 wsgi:app"]
