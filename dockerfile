FROM python:3.13-slim

# Копируем код и данные
COPY . .

RUN pip install --no-cache-dir uv

# Устанавливаем зависимости через uv С ФЛАГОМ --system
RUN uv pip install --system -r requirements.txt


CMD ["python", "main.py"]
