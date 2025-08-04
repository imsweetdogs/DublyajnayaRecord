# syntax=docker/dockerfile:1
FROM python:3.12-alpine

# Установка базовых зависимостей
RUN apk update && \
    apk add --no-cache build-base gcc musl-dev libffi-dev openssl-dev && \
    pip install --upgrade pip && \
    pip install uv 

# Установка рабочей директории
WORKDIR /app

# Копирование зависимостей проекта
COPY pyproject.toml uv.lock LICENSE README.md ./

# Копирование исходного кода
COPY src/ ./src/

# Команда по умолчанию с проверкой app_mode
ENTRYPOINT ["/bin/sh", "-c", "if [ \"$app_mode\" = 'webhook' ]; then exec uv run --all-extras start; else exec uv run --extra opt start; fi"]