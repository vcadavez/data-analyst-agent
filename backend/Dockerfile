FROM python:3.12-slim-bookworm

WORKDIR /app

COPY backend/requirements.txt ./backend/
RUN pip install --upgrade pip && pip install --no-cache-dir -r ./backend/requirements.txt && pip install langchain-community

COPY backend ./backend

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8000"]
