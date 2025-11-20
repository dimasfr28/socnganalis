FROM python:3.12-slim

WORKDIR /app

# Install netcat for healthchecks (psycopg2-binary doesn't need compilation)
RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN pip install --no-cache-dir \
    django \
    psycopg2-binary \
    pandas \
    matplotlib \
    openpyxl \
    requests

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
