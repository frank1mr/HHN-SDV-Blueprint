# Basis-Image mit Python
FROM python:3.10

# Arbeitsverzeichnis im Container setzen
WORKDIR /app

# Abhängigkeiten kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Skript kopieren
COPY main.py .

# Container dauerhaft laufen lassen
CMD ["python", "main.py"]



