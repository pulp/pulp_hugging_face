FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    git \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create pulp user
RUN useradd --create-home --shell /bin/bash pulp

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install pulpcore
RUN pip install pulpcore[postgres]

# Copy plugin source
COPY . .

# Install plugin in development mode
RUN pip install -e .

# Create necessary directories
RUN mkdir -p /var/lib/pulp/media /var/lib/pulp/tmp
RUN chown -R pulp:pulp /var/lib/pulp /app

# Switch to pulp user
USER pulp

# Set Python path
ENV PYTHONPATH=/app

# Default command
CMD ["pulp-manager", "runserver", "0.0.0.0:24817"]
