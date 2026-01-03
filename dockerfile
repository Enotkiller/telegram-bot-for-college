FROM python:3.13-slim

WORKDIR /project

# --- Ставим uv ---
RUN apt-get update && apt-get install -y curl
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# --- Сначала копируем только зависимости ---
COPY pyproject.toml uv.lock .python-version ./

# --- Ставим зависимости через uv ---
RUN uv sync

RUN uv venv --clear
# --- Потом копируем весь проект ---
COPY . .

# --- Команда запуска ---
CMD ["uv", "run", "main.py"]
