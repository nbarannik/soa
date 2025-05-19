FROM python:3.9-slim

WORKDIR /app

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

COPY ./proto ./proto
RUN python -m grpc_tools.protoc -I./proto --python_out=. --grpc_python_out=. ./proto/post_service.proto

ENV PYTHONPATH=/app
ENV POST_SERVICE_GRPC_HOST=post_service
ENV POST_SERVICE_GRPC_PORT=50051
ENV USER_SERVICE_URL=http://user_service:8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]