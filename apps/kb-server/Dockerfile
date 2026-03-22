FROM python:3.12-slim

WORKDIR /app

# Install git for repo sync
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY src/ src/

EXPOSE 8080

CMD ["python", "-m", "src.server"]
