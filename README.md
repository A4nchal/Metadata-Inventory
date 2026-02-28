# HTTP Metadata Inventory Service

## 📌 Project Overview

The **HTTP Metadata Inventory Service** is a FastAPI-based backend application that collects and stores HTTP metadata for a given URL.

For any provided URL, the service retrieves:

- HTTP headers  
- Cookies  
- Page source (static HTML content)  

The system maintains an internal inventory in MongoDB and supports asynchronous background metadata collection to ensure non-blocking API responses.

The project is fully containerized using Docker Compose and includes a comprehensive pytest-based test suite.

---

## 🏗 Architecture Overview

The project follows a layered architecture, ensuring clean separation of concerns and scalability.

```
app/
├── controller/ → API layer (FastAPI endpoints)
├── service/ → Business logic layer
├── repository/ → Database interaction layer
├── config/ → Configuration & database setup
├── dto/ → Request/Response models
├── tests/ → Pytest test suite
```

### Layer Responsibilities

#### Controller Layer
- Handles HTTP transport
- Performs input validation via Pydantic
- Returns appropriate HTTP status codes

#### Service Layer
- Contains business logic
- Manages background metadata collection
- Orchestrates repository and fetch services

#### Repository Layer
- Handles MongoDB persistence
- Provides indexed lookup by URL

#### Configuration Layer
- Manages environment-based configuration
- Handles MongoDB connection lifecycle
- Implements retry logic for DB startup delays

---

## ⚙️ System Design Highlights

- Asynchronous I/O using `async/await`
- Non-blocking background processing via FastAPI `BackgroundTasks`
- MongoDB with unique index on `url`
- Resilient database startup handling with retry mechanism
- Environment-based configuration
- Fully containerized with Docker Compose
- Clean separation of data, logic, and transport layers

---

## 🚀 How to Run

### Prerequisites

- Docker Desktop installed and running

### Start the Application

From the project root directory:

```bash
docker-compose up --build
```

This will start:
 - MongoDB container
 - FastAPI application container

### Access the API
 - Swagger UI:
   http://localhost:8000/docs

 - Health Check:
   http://localhost:8000/health

---

## 🧪 How to Test

### Run Tests Inside Docker

```bash
docker exec -it metadata_api pytest
```

You will see:

```code
5 passed
```

The test suite covers:

 - POST endpoint success case
 - GET cache hit
 - GET cache miss (202 behavior)
 - Invalid URL handling
 - Input validation

All external HTTP calls and database operations are mocked for deterministic unit testing.

---

## 📡 API Endpoints

### POST /metadata

Creates and stores metadata for a given URL.

#### Request Body

```JSON
{
  "url": "https://example.com"
}
```

#### Response (200 OK)

```JSON
{
  "url": "https://example.com",
  "headers": { ... },
  "cookies": { ... },
  "page_source": "<html>...</html>"
}
```

### GET /metadata

Retrieves metadata for a given URL.

#### Query Parameter

```code
?url=https://example.com
```

#### Possible Responses

 - 200 -	Metadata found in inventory
 - 202 -	Metadata collection initiated
 - 422 -	Invalid URL format
 - 502 -	Upstream service unreachable
 - 504 -	Upstream timeout

## 🧪 Example CURL Commands

### Create Metadata

```bash
curl -X POST http://localhost:8000/metadata \
-H "Content-Type: application/json" \
-d '{"url":"https://example.com"}'
``` 

### Retrieve Metadata (Cache Hit)

```bash
curl "http://localhost:8000/metadata?url=https://example.com"
```

### Retrieve Metadata (Cache Miss → 202)

```bash
curl "http://localhost:8000/metadata?url=https://newsite.com"
```

### Response:

```JSON
{
  "message": "Request accepted. Metadata collection initiated."
}
```

## 🧠 Design Decisions

### Asynchronous Architecture

The application uses async/await and httpx.AsyncClient to efficiently handle I/O-bound tasks such as HTTP calls and database operations.

### Non-Blocking Background Collection

When a GET request results in a cache miss:

 - The API immediately returns 202 Accepted
 - A background task is scheduled internally
 - No external self-calls or polling loops are used
 - The request-response cycle remains non-blocking

### Database Resilience

 - MongoDB connection uses retry logic
 - Unique index on url ensures efficient lookups
 - Graceful startup and shutdown lifecycle handling
   
### Validation Strategy

 - URL validation occurs at the controller layer using HttpUrl
 - Invalid URLs never reach the service layer
 - Proper HTTP status codes are returned
   
### Containerized Deployment

 - Uses Docker Compose for isolated local development
 - Environment variables control configuration
 - API communicates with MongoDB via Docker network hostname

---
