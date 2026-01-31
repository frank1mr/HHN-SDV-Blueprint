# Basis-Image mit Python
FROM python:3.10

# Arbeitsverzeichnis im Container setzen
WORKDIR /app

# Abhängigkeiten kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Skript kopieren
COPY app.py .

# Container dauerhaft laufen lassen
CMD ["python", "app.py"]