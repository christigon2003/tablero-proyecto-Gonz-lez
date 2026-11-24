FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8765

CMD ["sh", "-c", "solara run mi_proyecto/app.py --host=0.0.0.0 --port=${PORT:-8765}"]
