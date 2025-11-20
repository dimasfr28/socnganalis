FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for Node.js and Playwright
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    wget \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list \
    && apt-get update \
    && apt-get install nodejs -y \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir fastapi uvicorn pandas scikit-learn matplotlib openpyxl python-dotenv python-multipart

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
