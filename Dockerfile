FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir pydantic openai pyyaml fastapi uvicorn

COPY . .

EXPOSE 7860

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]