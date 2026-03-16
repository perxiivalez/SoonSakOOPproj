# ══════════════════════════════════════════════════════════════
# Dockerfile for SoonSak MCP Server
# ══════════════════════════════════════════════════════════════

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all Python files
COPY *.py .

# Expose port (optional, MCP uses stdio)
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8

# Run MCP server
CMD ["python", "mcp_server.py"]
