FROM python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y curl build-essential git && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Configure Poetry to not create virtual environment (since we're in Docker)
ENV POETRY_VENV_IN_PROJECT=false
ENV POETRY_NO_INTERACTION=1
ENV POETRY_CACHE_DIR=/tmp/poetry_cache

# Set working directory
WORKDIR /code

# Copy only pyproject.toml and poetry.lock first (for caching)
COPY pyproject.toml poetry.lock ./

# Install dependencies globally (no venv needed in container)
RUN poetry config virtualenvs.create false && \
    poetry install --only=main --no-root && \
    rm -rf $POETRY_CACHE_DIR

# Copy the rest of your application
COPY . .

# Expose port
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]