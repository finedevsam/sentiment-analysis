# Vue.js + Flask with Docker Compose

This project runs a Vue.js frontend and Flask backend using Docker Compose.

## Requirements
- Docker installed  
- Docker Compose installed  

## Project Structure
```
project-root/
│
├── backend/              # Flask app
│   ├── app.py
│   ├── requirements.txt
│   └── ...
│
├── dashboard/            # Vue.js app
│   ├── package.json
│   └── ...
│
├── backend.Dockerfile
├── frontend.Dockerfile
├── docker-compose.yml
└── README.md
```

## Setup

### 1. Clone the repository
```
git clone https://github.com/yourusername/yourproject.git
cd yourproject
```

### 2. Build and run services
```
docker-compose up --build
```

### 3. Access the services
- Frontend: http://localhost:8080  
- Backend API: http://localhost:5000  

## Docker Configuration

### docker-compose.yml
```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: backend.Dockerfile
    container_name: flask-backend
    ports:
      - "5000:5000"
    volumes:
      - ./backend:/app
    networks:
      - app-network

  frontend:
    build:
      context: .
      dockerfile: frontend.Dockerfile
    container_name: vue-frontend
    ports:
      - "8080:8080"
    volumes:
      - ./dashboard:/app
    networks:
      - app-network
    depends_on:
      - backend

networks:
  app-network:
    driver: bridge
```

### Backend Dockerfile (`backend.Dockerfile`)
```dockerfile
# Use official Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy backend source
COPY ./backend /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Flask port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
```

### Frontend Dockerfile (`frontend.Dockerfile`)
```dockerfile
# Build Stage
FROM node:20-alpine as build-stage

WORKDIR /app

COPY ./dashboard /app

RUN npm install && npm run build

# Production Stage
FROM nginx:stable-alpine as production-stage

COPY --from=build-stage /app/dist /usr/share/nginx/html


EXPOSE 80

CMD ["nginx", "-g", "daemon off;", "yarn", "serve"]
```

## Development
- Flask backend runs in debug mode if enabled in `app.py`  
- Vue.js frontend uses hot reload with mounted volume  

## Stopping services
```
docker-compose down
```
