FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies for mysqlclient
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Make the path explicit for the app
ENV GIT_BIN=/usr/bin/git

# Install Python dependencies
copy ./pyproject.toml ./
RUN uv sync

# Copy project
COPY . .

# Run migrations and start server
CMD ["sh", "-c", "uv run python manage.py migrate && uv run python manage.py runserver 0.0.0.0:8000"]
