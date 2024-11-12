FROM ghcr.io/astral-sh/uv:python3.10-alpine

# Set the working directory
WORKDIR /app

# Set the Env to production
ENV FLASK_ENV=production

# Copy the current directory contents into the container at /app
ADD . /app

# Install the packages
RUN uv sync --frozen

# Run the application
CMD ["uv", "run", "gunicorn", "-b", "0.0.0.0:5000", "app:app", "--workers=16"]