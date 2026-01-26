FROM python:3.12-slim

WORKDIR /app

# RUN apt-get update && apt-get install -y build-essential

# packaging metadata first (better caching)
COPY pyproject.toml ./

# install build backend + deps
RUN pip install --no-cache-dir .

# the actual source
COPY app/ app/

# run the server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]