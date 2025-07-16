# backend/Dockerfile
FROM python:3.11

# Set working directory
WORKDIR /app


# Install dependencies
RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

RUN uv sync --locked

# Copy the project code
COPY ./backend /app

# Expose the port
EXPOSE 8000

# Run migrations and start the Django development server
CMD ["sh", "-c", "uv run manage.py migrate && uv run manage.py runserver 0.0.0.0:8000"]
