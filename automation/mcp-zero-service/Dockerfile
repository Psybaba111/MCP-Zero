# Dockerfile for MCP-Zero Service
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy MCP-Zero and MCP-tools
COPY ../../MCP-zero /app/MCP-zero
COPY ../../MCP-tools /app/MCP-tools

# Expose port
EXPOSE 3001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3001/health || exit 1

# Run application
CMD ["python", "server.py"]