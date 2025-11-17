# ==========================
# Stage 1: Builder
# ==========================
FROM python:3.11-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies for building packages
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        gnupg2 \
        apt-transport-https \
        lsb-release \
        unixodbc-dev \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage caching
COPY requirements.txt .

# Install Python dependencies in builder
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# ==========================
# Stage 2: Final image
# ==========================
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/mssql-tools18/bin:$PATH"

# Install runtime dependencies + Microsoft ODBC driver
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        gnupg2 \
        apt-transport-https \
        lsb-release \
        unixodbc \
        ca-certificates \
    && curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /usr/share/keyrings/microsoft.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" \
       > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update && ACCEPT_EULA=Y apt-get install -y --no-install-recommends \
        msodbcsql18 \
        mssql-tools18 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy app code
COPY . .

# Copy wait-for-db script and make it executable
COPY wait-for-db.sh /wait-for-db.sh
RUN chmod +x /wait-for-db.sh

EXPOSE 8000

# Use the wait-for-db script as entrypoint
ENTRYPOINT ["/wait-for-db.sh"]

# Default command to run uvicorn (executed after wait-for-db.sh finishes)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
