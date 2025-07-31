FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY ./Envelopes ./Envelopes

# Optional: expose port 5000 (Flask default)
EXPOSE 5000

# Set environment variables needed for Flask to run properly
ENV FLASK_APP=./Envelopes/app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

CMD ["flask", "run"]