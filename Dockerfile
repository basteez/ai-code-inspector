FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    graphviz \
    graphviz-dev \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY requirements.txt .
COPY pyproject.toml .
COPY README.md .
COPY legacy_inspector/ ./legacy_inspector/
COPY prompts/ ./prompts/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -e .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Create volume mount point for code to analyze
VOLUME ["/code"]

# Set working directory to the mounted code folder
WORKDIR /code

# Default command
ENTRYPOINT ["legacy-inspector"]
CMD ["--help"]
