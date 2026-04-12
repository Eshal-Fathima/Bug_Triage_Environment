FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Default: run all tasks with gpt-4o-mini
# Override with: docker run ... python inference.py --task 0 --model gpt-4o
CMD ["python", "inference.py"]