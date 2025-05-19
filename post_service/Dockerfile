FROM python:3.9-slim

WORKDIR /app

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./proto ./proto
RUN python -m grpc_tools.protoc -I./proto --python_out=. --grpc_python_out=. ./proto/post_service.proto

COPY ./models ./models
COPY ./services ./services
COPY ./tests ./tests
COPY server.py .

ENV PYTHONPATH=/app
ENV POSTGRES_URL=postgresql://post_user:post_password@post_service_db:5432/post_db

CMD ["sh", "-c", "python -c 'from models.database import Base, engine; Base.metadata.create_all(bind=engine)' && python -u server.py"]