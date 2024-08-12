FROM python:3.10-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

WORKDIR /app/frontend
COPY frontend/package.json frontend/yarn.lock ./
RUN yarn install

COPY frontend/ .

RUN yarn build

RUN docker run -d --name redis -p 6379:6379 redis:7.0.4-alpine

RUN docker run -d --name postgres -p 5432:5432 -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password -e POSTGRES_DB=your_database_name postgres:14-alpine

EXPOSE 8000
EXPOSE 3000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
