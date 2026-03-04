FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (layer caching)
COPY app/server/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY app/ /app/

EXPOSE 5000

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 1 --timeout 120 --chdir /app/server app:app"]
