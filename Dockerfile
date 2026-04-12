FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run inference and keep output in a log file, then serve it
CMD python inference.py > /app/output.log 2>&1; cat /app/output.log; tail -f /dev/null