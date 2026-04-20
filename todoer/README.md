# Todo Management Application - Complete Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Quick Start](#quick-start)
5. [Building and Running](#building-and-running)
6. [API Documentation](#api-documentation)
7. [Frontend Features](#frontend-features)
8. [Testing](#testing)
9. [Docker Deployment](#docker-deployment)
10. [Database Configuration](#database-configuration)
11. [Commands Reference](#commands-reference)
12. [Troubleshooting](#troubleshooting)
13. [Project Structure](#project-structure)
14. [Technology Stack](#technology-stack)
15. [Future Enhancements](#future-enhancements)

---

## Project Overview

**Todo Management Application** is a modern, production-ready Spring Boot application designed for managing personal tasks and todos. It features a loosely-coupled architecture separating the API backend from the user interface, making it scalable and easily maintainable.

### Key Features
- ✅ **Create, Read, Update, Delete** todos with full CRUD operations
- 🔍 **Search and Filter** todos by status or keyword
- 🏷️ **Multiple Status Types**: PENDING, IN_PROGRESS, COMPLETED, CANCELLED
- 🎨 **Responsive Web UI** with real-time filtering and search
- 📱 **REST API** with comprehensive endpoints
- 🐳 **Docker Support** with multi-stage builds
- 🔄 **Loosely Coupled Architecture** - easily switch databases without code changes
- 🧪 **Comprehensive Test Suite** with 51+ unit tests and BDD scenarios
- ⏰ **Timestamps** - tracks creation and update times for each todo
- 🎯 **Clean Code** - follows SOLID principles and best practices

### Motivation
This application demonstrates how to build enterprise-grade applications using Spring Boot with:
- Clear separation of concerns (Repository → Service → Controller)
- Data Transfer Objects (DTOs) for API contracts
- Exception handling and error responses
- CORS configuration for frontend-backend communication
- Comprehensive testing at multiple layers

---

## Architecture

The application follows a **layered architecture** pattern with loose coupling:

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend UI (HTML/CSS/JS)                │
│                    (http://localhost:8080)                  │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   TodoController                            │
│            (HTTP Entry Point - 7 endpoints)                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   TodoService                               │
│            (Business Logic Layer - 7 methods)               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                TodoRepository (Interface)                   │
│       (Data Access - MongoRepository abstraction)           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  MongoDB 7.0 Database                       │
│         (Persistent, Scalable NoSQL Database)              │
└─────────────────────────────────────────────────────────────┘
```

### Design Principles

**1. Repository Pattern**
- Repository interface (`TodoRepository`) abstracts data access
- Uses **MongoRepository** for MongoDB operations
- Only repository layer knows about database implementation
- Switching databases requires: 1 dependency change + 1 configuration change
- Zero changes to Service or Controller layers

**2. Layered Architecture**
- **Controller**: HTTP handling, request/response mapping, CORS
- **Service**: Business logic, validation, data transformation
- **Repository**: Data access, queries, persistence
- **Model**: Entity definitions, JPA annotations
- **DTO**: Data Transfer Objects, API contracts

**3. Exception Handling**
- `GlobalExceptionHandler` centralizes error responses
- Consistent HTTP status codes (201 Create, 400 Bad Request, 404 Not Found, 500 Error)
- Meaningful error messages

**4. Loose Coupling Benefits**
- Frontend and backend are completely decoupled
- UI doesn't know about database structure
- Can change database without UI changes
- Can build mobile apps consuming same API

---

## Prerequisites

### Required
- **Java 21** (or higher)
  - Download: https://www.oracle.com/java/technologies/downloads/#java21
  - Verify: `java -version`
  
- **Maven 3.9.0** (or higher)
  - Download: https://maven.apache.org/download.cgi
  - Verify: `mvn -version`

- **Docker** (required for MongoDB and containerized deployment)
  - Download: https://www.docker.com/products/docker-desktop
  - Verify: `docker --version` and `docker compose --version`

- **MongoDB 7.0** (included in Docker Compose setup)
  - Automatically deployed when using `docker compose up`
  - Credentials: `admin / admin123`
  - Port: `27017`

### Recommended
- **Git** for version control
- **cURL** for testing API endpoints
- **IDE**: IntelliJ IDEA, VS Code, or Eclipse
- **MongoDB Compass** for database visualization (optional)

---

## Quick Start

### 1. Clone/Download the Project
```bash
cd ~/Documents/workspace/github/todoer
```

### 2. Using Docker Compose (Recommended)

The easiest way to run the application with MongoDB:

```bash
# Start all services (MongoDB + Application)
docker compose up

# Or run in background
docker compose up -d

# Check service status
docker compose ps
```

**What happens:**
- MongoDB 7.0 container starts and initializes
- Application waits for MongoDB health check
- Application starts on port 8080
- Data persists in `mongo-data` volume

**First run time**: ~20-30 seconds

### 3. Access the Application
- **UI**: http://localhost:8080
- **API Base**: http://localhost:8080/api/todos

### 4. Stop Services
```bash
# Stop all containers
docker compose down

# Remove containers and volumes (WARNING: deletes data)
docker compose down -v
```

---

## Building and Running (Local Development)

### Maven Commands

#### Clean Build
```bash
cd todoapp-api
mvn clean install
```

This will:
- Clean previous build artifacts
- Compile all Java source files
- Run all unit tests (with Flapdoodle embedded MongoDB)
- Package the application as a JAR file
- Place the JAR in `target/todoapp-api-1.0.0.jar`

**Build time**: ~30-45 seconds (first time with downloads)

#### Compile Only
```bash
mvn compile
```
Compiles Java source files to bytecode.

#### Run All Tests
```bash
mvn test
```
Runs all 51+ unit tests with Flapdoodle embedded MongoDB for database testing.

#### Package Only
```bash
mvn package -DskipTests
```
Packages application without running tests.
```bash
mvn test
```
Executes all 51 unit tests with BDD scenarios.

#### Build Without Tests
```bash
mvn clean package -DskipTests
```
Faster build if you just want to package.

#### Full Build with Tests
```bash
mvn clean install
```
Compiles, tests, and packages the application.

#### Run Application
```bash
# Option 1: Using Maven Spring Boot plugin
mvn spring-boot:run

# Option 2: Using JAR file (after build)
java -jar target/todoapp-api-1.0.0.jar

# Option 3: Run on different port
java -jar target/todoapp-api-1.0.0.jar --server.port=9090

# Option 4: Run with custom configuration
java -jar target/todoapp-api-1.0.0.jar --spring.jpa.database-platform=org.hibernate.dialect.PostgreSQL10Dialect
```

### Development Mode with Auto-reload
```bash
mvn spring-boot:run -Dspring-boot.run.arguments="--spring.devtools.restart.enabled=true"
```
This enables hot-reload when files change.

---

## API Documentation

The application exposes 7 REST endpoints for complete CRUD operations.

### Base URL
```
http://localhost:8080/api/todos
```

### 1. Create Todo (POST)

**Endpoint**: `POST /api/todos`

**Request Body**:
```json
{
  "title": "Buy Groceries",
  "description": "Milk, eggs, bread",
  "status": "PENDING"
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8080/api/todos \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy Groceries",
    "description": "Milk, eggs, bread",
    "status": "PENDING"
  }'
```

**Response** (HTTP 201 Created):
```json
{
  "id": 1,
  "title": "Buy Groceries",
  "description": "Milk, eggs, bread",
  "status": "PENDING",
  "createdAt": "2026-04-17T18:46:14",
  "updatedAt": "2026-04-17T18:46:14"
}
```

**Status Codes**:
- `201`: Todo created successfully
- `400`: Invalid request body
- `500`: Server error

---

### 2. Get All Todos (GET)

**Endpoint**: `GET /api/todos`

**cURL Example**:
```bash
curl http://localhost:8080/api/todos
```

**Response** (HTTP 200 OK):
```json
[
  {
    "id": 1,
    "title": "Buy Groceries",
    "description": "Milk, eggs, bread",
    "status": "PENDING",
    "createdAt": "2026-04-17T18:46:14",
    "updatedAt": "2026-04-17T18:46:14"
  },
  {
    "id": 2,
    "title": "Learn Spring Boot",
    "description": null,
    "status": "IN_PROGRESS",
    "createdAt": "2026-04-17T18:46:20",
    "updatedAt": "2026-04-17T18:46:20"
  }
]
```

**Status Codes**:
- `200`: Success
- `500`: Server error

---

### 3. Get Single Todo (GET)

**Endpoint**: `GET /api/todos/{id}`

**cURL Example**:
```bash
curl http://localhost:8080/api/todos/1
```

**Response** (HTTP 200 OK):
```json
{
  "id": 1,
  "title": "Buy Groceries",
  "description": "Milk, eggs, bread",
  "status": "PENDING",
  "createdAt": "2026-04-17T18:46:14",
  "updatedAt": "2026-04-17T18:46:14"
}
```

**Status Codes**:
- `200`: Todo found
- `404`: Todo not found
- `500`: Server error

---

### 4. Update Todo (PUT)

**Endpoint**: `PUT /api/todos/{id}`

**Request Body**:
```json
{
  "title": "Buy Groceries",
  "description": "Milk, eggs, bread, butter",
  "status": "IN_PROGRESS"
}
```

**cURL Example**:
```bash
curl -X PUT http://localhost:8080/api/todos/1 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy Groceries",
    "description": "Milk, eggs, bread, butter",
    "status": "IN_PROGRESS"
  }'
```

**Response** (HTTP 200 OK):
```json
{
  "id": 1,
  "title": "Buy Groceries",
  "description": "Milk, eggs, bread, butter",
  "status": "IN_PROGRESS",
  "createdAt": "2026-04-17T18:46:14",
  "updatedAt": "2026-04-17T18:46:25"
}
```

**Status Codes**:
- `200`: Todo updated successfully
- `400`: Invalid request body
- `404`: Todo not found
- `500`: Server error

---

### 5. Delete Todo (DELETE)

**Endpoint**: `DELETE /api/todos/{id}`

**cURL Example**:
```bash
curl -X DELETE http://localhost:8080/api/todos/1
```

**Response** (HTTP 204 No Content):
```
(empty body)
```

**Status Codes**:
- `204`: Todo deleted successfully
- `404`: Todo not found
- `500`: Server error

---

### 6. Filter Todos by Status (GET with Query Parameter)

**Endpoint**: `GET /api/todos?status=PENDING`

**Available Status Values**:
- `PENDING` - Not started yet
- `IN_PROGRESS` - Currently being worked on
- `COMPLETED` - Finished
- `CANCELLED` - Abandoned

**cURL Example**:
```bash
# Get all pending todos
curl "http://localhost:8080/api/todos?status=PENDING"

# Get all completed todos
curl "http://localhost:8080/api/todos?status=COMPLETED"

# Get all in-progress todos
curl "http://localhost:8080/api/todos?status=IN_PROGRESS"

# Get all cancelled todos
curl "http://localhost:8080/api/todos?status=CANCELLED"
```

**Response** (HTTP 200 OK):
```json
[
  {
    "id": 1,
    "title": "Buy Groceries",
    "description": "Milk, eggs, bread",
    "status": "PENDING",
    "createdAt": "2026-04-17T18:46:14",
    "updatedAt": "2026-04-17T18:46:14"
  }
]
```

**Status Codes**:
- `200`: Success (returns empty array if no todos match)
- `400`: Invalid status value
- `500`: Server error

---

### 7. Search Todos by Keyword (GET with Query Parameter)

**Endpoint**: `GET /api/todos?search=keyword`

**Search Behavior**:
- Case-insensitive search
- Searches in todo title only
- Returns all todos containing the keyword

**cURL Example**:
```bash
# Search for todos containing "groceries"
curl "http://localhost:8080/api/todos?search=groceries"

# Search is case-insensitive
curl "http://localhost:8080/api/todos?search=GROCERIES"

# Multi-word search (searches for todos containing "Buy")
curl "http://localhost:8080/api/todos?search=Buy"
```

**Response** (HTTP 200 OK):
```json
[
  {
    "id": 1,
    "title": "Buy Groceries",
    "description": "Milk, eggs, bread",
    "status": "PENDING",
    "createdAt": "2026-04-17T18:46:14",
    "updatedAt": "2026-04-17T18:46:14"
  }
]
```

**Status Codes**:
- `200`: Success (returns empty array if no match)
- `500`: Server error

---

### CORS Configuration

The API supports Cross-Origin Resource Sharing (CORS) for frontend communication.

**Current Configuration**:
- Allows requests from all origins (*)
- Allowed methods: GET, POST, PUT, DELETE, OPTIONS
- Allowed headers: Content-Type, Authorization

**Note**: For production, restrict origins in `CorsConfig.java`:
```java
allowedOrigins = {"https://yourdomain.com", "https://app.yourdomain.com"}
```

---

### Error Response Format

All errors follow a consistent format:

```json
{
  "message": "Error description",
  "status": 404,
  "timestamp": "2026-04-17T18:46:14"
}
```

**Common Error Scenarios**:

1. **Todo Not Found** (404):
```json
{
  "message": "Todo not found with id: 999",
  "status": 404,
  "timestamp": "2026-04-17T18:46:14"
}
```

2. **Invalid Request** (400):
```json
{
  "message": "Bad request: [field validation details]",
  "status": 400,
  "timestamp": "2026-04-17T18:46:14"
}
```

3. **Server Error** (500):
```json
{
  "message": "Internal server error",
  "status": 500,
  "timestamp": "2026-04-17T18:46:14"
}
```

---

## Frontend Features

### User Interface

The frontend is a **single-page application (SPA)** with no build step required. It's served as static HTML/CSS/JavaScript.

**Access**: http://localhost:8080

### Features

1. **Create Todos**
   - Form to enter title, description, and status
   - Real-time validation
   - Immediate feedback on creation

2. **View All Todos**
   - List of all todos with color-coded status badges
   - Shows creation and update timestamps
   - Displays total count

3. **Search Todos**
   - Real-time search by keyword
   - Case-insensitive matching
   - Filters results as you type

4. **Filter by Status**
   - Dropdown to filter by status (All, Pending, In Progress, Completed, Cancelled)
   - Color-coded status indicators
   - Shows filtered count

5. **Edit Todos**
   - Click on any todo to edit
   - Update title, description, or status
   - Timestamps update automatically

6. **Delete Todos**
   - Delete button for each todo
   - Confirmation before deletion
   - Instant update in list

7. **Status Badges**
   - **PENDING** (Yellow): Task waiting to start
   - **IN_PROGRESS** (Blue): Task being worked on
   - **COMPLETED** (Green): Task finished
   - **CANCELLED** (Red): Task abandoned

### UI/UX Design

- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Color-coded Status**: Visual indicators for quick scanning
- **Real-time Updates**: No page refresh needed
- **Keyboard Friendly**: Tab navigation, Enter to submit
- **Accessible**: Semantic HTML, ARIA labels
- **Modern Design**: Clean interface with subtle gradients and animations

---

## Testing

The application includes a comprehensive test suite with **51 unit tests** covering all scenarios.

### Test Coverage

#### 1. Controller Tests (26 tests)
- **Create Todo**: Success, validation, edge cases
- **Get Todo**: Success, not found, empty list
- **Filter by Status**: All 4 status types, empty results
- **Search**: Keyword match, case-insensitive, special characters
- **Update Todo**: Success, not found, all field updates
- **Delete Todo**: Success, not found, verification
- **CORS & Error Handling**: Cross-origin requests, error responses

**Location**: `src/test/java/com/todoapp/controller/TodoControllerTest.java`

#### 2. Service Tests (25 tests)
- **Create**: With all fields, default status, timestamps, empty description
- **Get**: By ID, all todos, by status, empty results
- **Search**: By keyword, case-insensitive, special characters, no match
- **Update**: Success, not found, individual fields, all fields
- **Delete**: Success, not found, verification
- **Edge Cases**: Null description, multiple same-title todos, status transitions

**Location**: `src/test/java/com/todoapp/service/TodoServiceTest.java`

### Running Tests

#### Run All Tests
```bash
mvn test
```

**Output**:
```
[INFO] Tests run: 51, Failures: 0, Errors: 0, Skipped: 0
[INFO] BUILD SUCCESS
```

#### Run Specific Test Class
```bash
mvn test -Dtest=TodoControllerTest
mvn test -Dtest=TodoServiceTest
```

#### Run Specific Test Method
```bash
mvn test -Dtest=TodoControllerTest#testCreateTodoSuccess
```

#### Generate Test Report
```bash
mvn surefire-report:report
```

Report generated at: `target/site/surefire-report.html`

### BDD Scenarios

The application uses Gherkin syntax for BDD-style test scenarios. These describe the application behavior in human-readable format.

**Scenarios included** (in `src/test/resources/features/todo.feature`):

#### Create Scenarios
- Create todo with all fields
- Create todo with only required fields
- Create todo with different status types
- Create multiple todos sequentially
- Create todo with empty description

#### Read Scenarios
- Get all todos
- Get specific todo by ID
- Get non-existent todo (error case)
- Get todos when database is empty

#### Filter Scenarios
- Filter by PENDING status
- Filter by COMPLETED status
- Filter by IN_PROGRESS status
- Filter by CANCELLED status
- Filter with no results

#### Search Scenarios
- Search by keyword
- Case-insensitive search
- Search with no matching results
- Search with multiple matches

#### Update Scenarios
- Update todo title
- Update todo status
- Update all fields
- Update non-existent todo (error case)
- Status transitions

#### Delete Scenarios
- Delete todo
- Delete non-existent todo (error case)
- Delete multiple todos
- Delete and verify it's gone

#### Edge Cases
- Very long titles (500 characters)
- Special characters
- Invalid JSON
- Concurrent operations

#### Integration Scenarios
- Complete workflow: Create → Update → Search → Delete
- Bulk operations
- Data persistence

### Test Execution Flow

1. **Setup Phase** (BeforeEach)
   - Create test data
   - Initialize mocks
   - Configure expected behaviors

2. **Execution Phase**
   - Call API endpoints or service methods
   - Perform operations

3. **Verification Phase**
   - Assert results match expectations
   - Verify method calls were made
   - Check error handling

4. **Teardown Phase** (Automatic)
   - Clean up resources
   - Reset mocks

### Mocking Strategy

- **Controller Tests**: Service layer mocked using `@MockBean`
- **Service Tests**: Repository layer mocked using `@Mock`
- **Integration Tests**: Real H2 database used for end-to-end verification

This allows testing each layer in isolation while ensuring all layers work together.

---

## Docker Deployment

The application is fully containerized with Docker and includes MongoDB for production-ready deployment.

### Prerequisites
- Docker installed: `docker --version`
- Docker Compose: `docker compose --version`

### Quick Start with Docker Compose (Recommended)

```bash
cd /Users/pramod/Documents/workspace/github/todoer

# Start all services
docker compose up

# Or run in background
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f

# Stop services
docker compose down

# Remove services and volumes (WARNING: deletes data)
docker compose down -v
```

**Services Started:**
1. **MongoDB 7.0** - Port 27017
   - Credentials: admin/admin123
   - Database: todoapp
   - Persistent volume: mongo-data

2. **Todo Application** - Port 8080
   - Spring Boot application
   - Connected to MongoDB
   - Health checks enabled

**Access**: http://localhost:8080

### Docker Compose Configuration

The `docker-compose.yml` file orchestrates both services:

```yaml
version: '3.8'

services:
  mongo:
    image: mongo:7.0
    container_name: todoapp-mongo
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: admin123
      MONGO_INITDB_DATABASE: todoapp
    volumes:
      - mongo-data:/data/db
    restart: unless-stopped
    healthcheck:
      test: echo 'db.runCommand("ping").ok' | mongosh localhost:27017/test --quiet
      interval: 10s
      timeout: 5s
      retries: 5

  todoapp:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: todoapp-api
    ports:
      - "8080:8080"
    environment:
      - SPRING_PROFILES_ACTIVE=prod
      - SPRING_DATA_MONGODB_URI=mongodb://admin:admin123@mongo:27017/todoapp?authSource=admin
      - SPRING_DATA_MONGODB_AUTO_INDEX_CREATION=true
    depends_on:
      mongo:
        condition: service_healthy
    restart: unless-stopped

volumes:
  mongo-data:
```

### Manual Docker Build and Run

```bash
# Build image
docker build -t todoapp:latest .

# Run container (requires MongoDB running separately)
docker run -d -p 8080:8080 \
  -e SPRING_DATA_MONGODB_URI=mongodb://admin:admin123@mongo:27017/todoapp?authSource=admin \
  --name todoapp todoapp:latest

# Access logs
docker logs todoapp

# Stop container
docker stop todoapp

# Remove container
docker rm todoapp
```

### Dockerfile Details

The `Dockerfile` uses **multi-stage build** for optimization:

**Stage 1: Builder**
- Base image: `maven:3.9-eclipse-temurin-21`
- Resolves Maven dependencies
- Compiles and packages the application
- Creates `todoapp-api-1.0.0.jar`

**Stage 2: Runtime**
- Base image: `eclipse-temurin:21-jre-jammy`
- Only includes the JAR and static files
- Final image size: ~250MB (optimized with multi-stage)

**Features**:
- Port 8080 exposed
- Health check every 30 seconds
- Automatic restart on failure
- MongoDB connection required (no embedded database)

### Deploying to Production

For production deployment:

1. **Use Persistent Database**
   - MongoDB is already persistent (configured with volumes)
   - For scaling, consider MongoDB Atlas or managed service

2. **Secure Credentials**
   - Never hardcode credentials in code
   - Use environment variables or secrets management
   - For production: use strong passwords instead of admin123

3. **Configure CORS**
   - Update `CorsConfig.java` with specific allowed origins
   - Restrict to your frontend domain only

4. **Enable HTTPS**
   - Add SSL certificates to Docker image
   - Configure Tomcat SSL settings
   - Map port 443

5. **Resource Limits**
   - Set memory limits in Docker Compose
   - Configure JVM heap size: `-Xmx512m -Xms256m`

6. **Logging and Monitoring**
   - Use Docker logging drivers (ELK, Splunk, etc.)
   - Monitor container health
   - Set up alerts

7. **Use Docker Registry**
   - Push image to Docker Hub or private registry
   - Pull image during deployment
   - Example: `docker.io/yourregistry/todoapp:v1.0.0`

---

## Database Configuration

The application uses **MongoDB 7.0** by default, deployed via Docker Compose. It's designed to work with any NoSQL or SQL database.

### Current Configuration (MongoDB 7.0)

**Docker Compose Setup** (`docker-compose.yml`):
```yaml
services:
  mongo:
    image: mongo:7.0
    container_name: todoapp-mongo
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: admin123
      MONGO_INITDB_DATABASE: todoapp
    volumes:
      - mongo-data:/data/db
```

**Spring Properties** (`application.properties`):
```properties
spring.data.mongodb.uri=mongodb://admin:admin123@mongo:27017/todoapp?authSource=admin
spring.data.mongodb.auto-index-creation=true
```

**Characteristics**:
- ✅ Persistent storage in Docker volume (`mongo-data`)
- ✅ Automatic initialization with credentials
- ✅ Health checks ensure MongoDB is ready before app starts
- ✅ Production-ready with authentication
- ✅ Data persists across container restarts
- ✅ Access MongoDB shell: `docker compose exec mongo mongosh -u admin -p admin123`

### Testing with Flapdoodle

The application uses **Flapdoodle Embedded MongoDB** for unit tests:

**Dependency** (`pom.xml`):
```xml
<dependency>
    <groupId>de.flapdoodle.embed</groupId>
    <artifactId>de.flapdoodle.embed.mongo.spring30x</artifactId>
    <version>4.5.2</version>
    <scope>test</scope>
</dependency>
```

**Test Configuration**:
- Automatically starts embedded MongoDB during test execution
- Tests have full CRUD operations against MongoDB
- No need for Docker or external database during local testing
- Runs `mvn test` with full database testing

### MongoDB Commands

#### Access MongoDB Shell
```bash
# From Docker container
docker compose exec mongo mongosh -u admin -p admin123

# Check databases
> show dbs

# Switch to todoapp database
> use todoapp

# View collections
> show collections

# Query todos
> db.todos.find()

# Count todos
> db.todos.countDocuments()
```

#### Backup Database
```bash
docker compose exec mongo mongodump -u admin -p admin123 -d todoapp -o /backup
```

#### Restore Database
```bash
docker compose exec mongo mongorestore -u admin -p admin123 /backup
```

### Switching to PostgreSQL (Alternative)

If you prefer SQL databases, you can switch to PostgreSQL:

#### Step 1: Update pom.xml
```xml
<!-- Remove MongoDB dependency -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-mongodb</artifactId>
</dependency>

<!-- Add PostgreSQL dependency -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-jpa</artifactId>
</dependency>
<dependency>
    <groupId>org.postgresql</groupId>
    <artifactId>postgresql</artifactId>
    <version>42.7.0</version>
    <scope>runtime</scope>
</dependency>
```

#### Step 2: Update Repository
Change `MongoRepository<Todo, String>` to `JpaRepository<Todo, Long>`

#### Step 3: Update Todo Entity
Convert from MongoDB `@Document` to JPA `@Entity`

#### Step 4: Update application.properties
```properties
spring.datasource.url=jdbc:postgresql://localhost:5432/todoapp
spring.datasource.username=postgres
spring.datasource.password=your_password
spring.jpa.hibernate.ddl-auto=update
```

### Switching to MySQL

Similar to PostgreSQL, but with MySQL-specific dependencies and configuration.
```

#### Step 4: Rebuild and Run
```bash
mvn clean install
java -jar target/todoapp-api-1.0.0.jar
```

**Key Changes**:
- Only 2 files modified: `pom.xml` and `application.properties`
- Zero code changes in Java classes
- All endpoints work identically
- Data persists across restarts

### Switching to MySQL

#### Step 1: Update pom.xml
```xml
<!-- Remove H2 dependency -->
<!-- Add MySQL dependency -->
<dependency>
    <groupId>com.mysql</groupId>
    <artifactId>mysql-connector-j</artifactId>
    <version>8.0.33</version>
    <scope>runtime</scope>
</dependency>
```

#### Step 2: Update application.properties
```properties
spring.datasource.url=jdbc:mysql://localhost:3306/todoapp
spring.datasource.username=root
spring.datasource.password=your_password
spring.datasource.driver-class-name=com.mysql.cj.jdbc.Driver
spring.jpa.database-platform=org.hibernate.dialect.MySQL8Dialect
spring.jpa.hibernate.ddl-auto=update
```

#### Step 3: Create Database
```bash
# Login to MySQL
mysql -u root -p

# Create database
CREATE DATABASE todoapp;
```

### Switching to MongoDB

For MongoDB, a different approach is needed:

#### Step 1: Update pom.xml
```xml
<!-- Replace JPA dependencies with Spring Data MongoDB -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-mongodb</artifactId>
</dependency>
```

#### Step 2: Update Models
Replace `@Entity` and `@Table` with `@Document`

#### Step 3: Update Repository
Extend `MongoRepository` instead of `JpaRepository`

#### Step 4: Update application.properties
```properties
spring.data.mongodb.uri=mongodb://localhost:27017/todoapp
```

---

## Migration from H2 to MongoDB

This section documents the migration from H2 in-memory database to MongoDB for production-ready deployment.

### What Changed

#### 1. Dependencies
- **Removed**: `com.h2database:h2`
- **Added**: `org.springframework.boot:spring-boot-starter-data-mongodb`
- **Added**: `de.flapdoodle.embed:de.flapdoodle.embed.mongo.spring30x` (for testing)

#### 2. Code Changes

**Model Layer** (`Todo.java`):
```java
// Before (H2 with JPA)
@Entity
@Table(name = "todos")
private Long id;

// After (MongoDB)
@Document(collection = "todos")
private String id;
```

**Repository Layer** (`TodoRepository.java`):
```java
// Before
extends JpaRepository<Todo, Long>

// After
extends MongoRepository<Todo, String>
```

**Service Layer** (`TodoService.java`):
- Changed method signatures from `Long id` to `String id`
- Added manual timestamp management (no `@PrePersist`, `@PreUpdate`)

**Controller Layer** (`TodoController.java`):
- Updated path variables from `@PathVariable Long id` to `@PathVariable String id`

**DTO Layer** (`TodoDTO.java`):
- Changed ID type from `Long` to `String`

#### 3. Configuration
```properties
# Before
spring.datasource.url=jdbc:h2:mem:testdb
spring.jpa.hibernate.ddl-auto=update

# After
spring.data.mongodb.uri=mongodb://admin:admin123@mongo:27017/todoapp?authSource=admin
spring.data.mongodb.auto-index-creation=true
```

#### 4. Docker Compose
- Added MongoDB 7.0 service with persistent volume
- Added health checks for both services
- Application waits for MongoDB to be healthy before starting

### Benefits of MongoDB

✅ **Persistent Storage**: Data survives container restarts  
✅ **Scalability**: Built-in sharding and replication  
✅ **Flexibility**: Schema-less design allows evolution  
✅ **Production Ready**: Includes authentication and encryption  
✅ **Testing**: Flapdoodle provides embedded MongoDB for tests  
✅ **NoSQL**: JSON-like documents match Java objects naturally  

### Testing with Flapdoodle

Flapdoodle Embedded MongoDB is automatically used during `mvn test`:
- Downloads and starts embedded MongoDB
- Runs all tests against real MongoDB
- Cleans up after tests complete
- No external dependencies needed for testing

---

## Commands Reference

### Maven Commands

```bash
# Build project with tests
mvn clean install

# Build without tests (faster)
mvn clean package -DskipTests

# Run tests only
mvn test

# Run specific test
mvn test -Dtest=TodoControllerTest

# Generate test reports
mvn surefire-report:report

# Generate JavaDoc
mvn javadoc:javadoc

# Check dependencies
mvn dependency:tree

# Clean build artifacts
mvn clean

# Run application
mvn spring-boot:run
```

### Java Commands

```bash
# Compile and run (after mvn package)
java -jar target/todoapp-api-1.0.0.jar

# Run on custom port
java -jar target/todoapp-api-1.0.0.jar --server.port=9090

# Run with custom database URL
java -jar target/todoapp-api-1.0.0.jar --spring.datasource.url=jdbc:h2:file:~/todoapp_db

# Enable debug logging
java -jar target/todoapp-api-1.0.0.jar --logging.level.root=DEBUG

# Run as background process
nohup java -jar target/todoapp-api-1.0.0.jar > app.log 2>&1 &
```

### Docker Commands

```bash
# Build Docker image
docker build -t todoapp:latest .

# Run container
docker run -d -p 8080:8080 --name todoapp todoapp:latest

# View logs
docker logs todoapp

# Stop container
docker stop todoapp

# Remove container
docker rm todoapp

# Using Docker Compose
docker-compose up --build
docker-compose down
docker-compose ps
```

### cURL Commands (API Testing)

```bash
# Create todo
curl -X POST http://localhost:8080/api/todos \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","description":"Desc","status":"PENDING"}'

# Get all todos
curl http://localhost:8080/api/todos

# Get single todo
curl http://localhost:8080/api/todos/1

# Filter by status
curl "http://localhost:8080/api/todos?status=PENDING"

# Search todos
curl "http://localhost:8080/api/todos?search=keyword"

# Update todo
curl -X PUT http://localhost:8080/api/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Updated","description":"New","status":"IN_PROGRESS"}'

# Delete todo
curl -X DELETE http://localhost:8080/api/todos/1

# Pretty print response
curl http://localhost:8080/api/todos | jq .
```

### File System Commands

```bash
# Navigate to project
cd ~/Documents/workspace/github/todoer

# View directory structure
ls -la

# View file contents
cat README.md

# Edit file (macOS)
nano application.properties

# Search for text in files
grep -r "TODO" src/

# Find all Java files
find . -name "*.java"
```

---

## Troubleshooting

### Issue: Maven not found
**Error**: `mvn: command not found`

**Solution**:
```bash
# Install Maven with Homebrew (macOS)
brew install maven

# Verify installation
mvn -version
```

### Issue: Java version incompatible
**Error**: `Java version is not 21`

**Solution**:
```bash
# Check current version
java -version

# Install Java 21 (macOS)
brew install java@21

# Set as default
export JAVA_HOME=$(/usr/libexec/java_home -v 21)

# Verify
java -version
```

### Issue: Port 8080 already in use
**Error**: `Address already in use`

**Solution**:
```bash
# Find process using port 8080
lsof -i :8080

# Kill process (replace PID)
kill -9 <PID>

# Or run on different port
java -jar target/todoapp-api-1.0.0.jar --server.port=9090
```

### Issue: Application won't start
**Error**: `Connection refused` or timeout

**Solution**:
1. Check if all dependencies are installed: `mvn dependency:resolve`
2. Verify Java 21 is installed: `java -version`
3. Check logs for specific errors: `tail -50 nohup.out`
4. Try rebuilding: `mvn clean install`

### Issue: Tests failing
**Error**: `TEST FAILED`

**Solution**:
```bash
# Run tests with verbose output
mvn test -e

# Run specific failing test
mvn test -Dtest=TestClassName

# Run without parallel execution
mvn test -DparallelTestClasses=false
```

### Issue: MongoDB connection failed
**Error**: `Connection refused: connect` or `Unauthorized`

**Solution**:
```bash
# Check if MongoDB container is running
docker compose ps

# Verify MongoDB is healthy
docker compose logs mongo

# Restart services
docker compose down
docker compose up -d

# Check connection URI in application.properties
# Should be: mongodb://admin:admin123@mongo:27017/todoapp?authSource=admin

# Test MongoDB connection
docker compose exec mongo mongosh -u admin -p admin123 --eval "db.adminCommand('ping')"
```

### Issue: Application container fails to start
**Error**: Container exits immediately or shows "Unhealthy"

**Solution**:
```bash
# Check application logs
docker compose logs todoapp

# Look for MongoDB connection errors
# Ensure MongoDB is healthy first (see above)

# Restart all services
docker compose restart

# If still failing, rebuild image
docker compose build --no-cache
docker compose up -d
```

### Issue: Port 8080 already in use
**Error**: `Address already in use` or `Bind failed`

**Solution**:
```bash
# Find process using port 8080
lsof -i :8080

# Kill process (replace PID)
kill -9 <PID>

# Or map to different port in docker-compose.yml
# Change: ports: ["9090:8080"]

# Or run local JAR on different port
java -jar target/todoapp-api-1.0.0.jar --server.port=9090
```

### Issue: Port 27017 already in use (MongoDB)
**Error**: MongoDB container fails to start

**Solution**:
```bash
# Find what's using port 27017
lsof -i :27017

# Stop old MongoDB containers
docker stop todoapp-mongo

# Remove old containers
docker rm todoapp-mongo

# Restart compose
docker compose down -v
docker compose up -d
```

### Issue: Docker build fails with Maven
**Error**: `maven:3.9-eclipse-temurin-21: not found`

**Solution**:
```bash
# Verify Docker images available
docker pull maven:3.9-eclipse-temurin-21
docker pull eclipse-temurin:21-jre-jammy

# Retry build
docker compose build --no-cache

# Or check your internet connection and Docker Hub access
```

### Issue: Maven dependency resolution fails
**Error**: `Failed to execute goal on project`

**Solution**:
```bash
# Clear Maven cache
rm -rf ~/.m2/repository

# Resolve dependencies
mvn dependency:resolve -U

# Rebuild
mvn clean install
```

### Issue: Java version incompatible
**Error**: `Java version is not 21` or `Unsupported class-file format`

**Solution**:
```bash
# Check current version
java -version

# Install Java 21 (macOS)
brew install java@21

# Set as default
export JAVA_HOME=$(/usr/libexec/java_home -v 21)

# Verify
java -version

# Rebuild project
mvn clean install
```

### Issue: CORS errors in frontend
**Error**: `Access-Control-Allow-Origin` error

**Solution**:
1. Verify application is running: `curl http://localhost:8080`
2. Check `CorsConfig.java` allows your origin
3. For local development, current config allows all origins (*)
4. For production, update `CorsConfig.java` with specific origins

### Issue: API returns empty results
**Error**: `GET /api/todos` returns `[]` even after creating todos

**Solution**:
```bash
# Check if MongoDB has data
docker compose exec mongo mongosh -u admin -p admin123

# In MongoDB shell
use todoapp
db.todos.find()
db.todos.countDocuments()

# If empty, the database needs data to be created
# Use the UI or API to create todos:
curl -X POST http://localhost:8080/api/todos \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","status":"PENDING"}'
```

---

## Project Structure

```
todoer/
├── todoapp-api/                              # Backend Spring Boot application
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/todoapp/
│   │   │   │   ├── TodoAppApplication.java  # Spring Boot entry point
│   │   │   │   ├── controller/
│   │   │   │   │   └── TodoController.java  # REST endpoints (7 methods)
│   │   │   │   ├── service/
│   │   │   │   │   └── TodoService.java     # Business logic (7 methods)
│   │   │   │   ├── repository/
│   │   │   │   │   └── TodoRepository.java  # Data access interface
│   │   │   │   ├── model/
│   │   │   │   │   ├── Todo.java            # MongoDB document
│   │   │   │   │   └── TodoStatus.java      # Status enum (4 types)
│   │   │   │   ├── dto/
│   │   │   │   │   ├── TodoDTO.java         # Data transfer object
│   │   │   │   │   └── CreateTodoRequest.java # API request DTO
│   │   │   │   ├── exception/
│   │   │   │   │   ├── TodoNotFoundException.java
│   │   │   │   │   └── GlobalExceptionHandler.java
│   │   │   │   └── config/
│   │   │   │       └── CorsConfig.java      # CORS configuration
│   │   │   ├── resources/
│   │   │   │   ├── application.properties   # Spring Boot config
│   │   │   │   └── static/
│   │   │   │       └── index.html           # Frontend UI (SPA)
│   │   │   └── templates/                   # (empty, using static HTML)
│   │   ├── test/
│   │   │   ├── java/com/todoapp/
│   │   │   │   ├── controller/
│   │   │   │   │   └── TodoControllerTest.java (26 tests)
│   │   │   │   └── service/
│   │   │   │       └── TodoServiceTest.java (25 tests)
│   │   │   └── resources/
│   │   │       └── features/
│   │   │           └── todo.feature         # BDD scenarios (40+ scenarios)
│   │   └── pom.xml                          # Maven dependencies
│   └── target/
│       └── todoapp-api-1.0.0.jar            # Compiled JAR (after mvn package)
├── todoapp-ui/                              # (Legacy, UI moved to static/)
├── Dockerfile                               # Multi-stage Docker build
├── docker-compose.yml                       # Docker Compose orchestration
├── README.md                                # This file
└── .gitignore                               # Git ignore rules
```

### File Descriptions

**Backend Files** (11 Java classes + 1 Test class):

1. **TodoAppApplication.java** (5 lines)
   - Spring Boot entry point
   - Starts Tomcat on port 8080

2. **TodoController.java** (120 lines)
   - 7 REST endpoints
   - HTTP request handling
   - CORS enabled

3. **TodoService.java** (90 lines)
   - Business logic
   - 7 methods for CRUD + search/filter
   - Logging via Slf4j

4. **TodoRepository.java** (10 lines)
   - JpaRepository extension
   - 2 custom query methods
   - Database abstraction

5. **Todo.java** (40 lines)
   - JPA entity
   - Represents todo in database
   - Timestamps automatically managed

6. **TodoStatus.java** (10 lines)
   - Enum with 4 status types
   - PENDING, IN_PROGRESS, COMPLETED, CANCELLED

7. **TodoDTO.java** (30 lines)
   - API response object
   - Excludes sensitive fields

8. **CreateTodoRequest.java** (20 lines)
   - API request object
   - Input validation

9. **TodoNotFoundException.java** (15 lines)
   - Custom exception
   - 404 error responses

10. **GlobalExceptionHandler.java** (40 lines)
    - Centralized error handling
    - Consistent error format

11. **CorsConfig.java** (25 lines)
    - CORS configuration
    - Allows cross-origin requests

12. **TodoControllerTest.java** (400 lines)
    - 26 unit tests
    - Tests all endpoints
    - Uses MockMvc and Mockito

**Configuration Files**:

1. **pom.xml**
   - Maven build configuration
   - Java 21 target
   - Spring Boot 3.2.0
   - All dependencies specified

2. **application.properties**
   - Spring Boot configuration
   - Database settings
   - Logging configuration
   - Server port (8080)

3. **Dockerfile**
   - Multi-stage build
   - Builder + runtime stages
   - Optimized for size

4. **docker-compose.yml**
   - Container orchestration
   - Port mapping
   - Volume configuration

**Frontend**:

1. **index.html** (1000+ lines)
   - Single-page application
   - Embedded CSS (~400 lines)
   - Embedded JavaScript (~400 lines)
   - Responsive design

---

## Technology Stack

### Backend
- **Framework**: Spring Boot 3.2.0
- **Language**: Java 21
- **Build Tool**: Maven 3.9+
- **Web Server**: Apache Tomcat (embedded)
- **Database**: MongoDB 7.0 (with Spring Data MongoDB)
- **Testing Database**: Flapdoodle Embedded MongoDB
- **Logging**: SLF4J with Logback
- **Testing**: JUnit 5, Mockito, Spring Test
- **JSON**: Jackson
- **Dependency Injection**: Lombok

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Responsive design, gradients, animations
- **JavaScript**: Vanilla JS (ES6+, no framework)
- **API**: Fetch API for HTTP requests
- **Architecture**: Single-page application (SPA)

### DevOps & Containerization
- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Docker Compose
- **Database**: MongoDB 7.0 (official image)
- **Java Runtime**: Eclipse Temurin (OpenJDK) 21
- **Base Images**: 
  - Builder: `maven:3.9-eclipse-temurin-21`
  - Runtime: `eclipse-temurin:21-jre-jammy`
  - Database: `mongo:7.0`

### Testing
- **Unit Testing**: JUnit 5
- **Mocking**: Mockito
- **Spring Testing**: @WebMvcTest, @SpringBootTest
- **Embedded Database**: Flapdoodle MongoDB
- **BDD**: Gherkin/Cucumber syntax in test scenarios

### Key Dependencies
```xml
<!-- Spring Data MongoDB -->
<artifactId>spring-boot-starter-data-mongodb</artifactId>

<!-- Flapdoodle for Testing -->
<artifactId>de.flapdoodle.embed.mongo.spring30x</artifactId>
<version>4.5.2</version>

<!-- Lombok -->
<artifactId>lombok</artifactId>

<!-- Spring Boot Web -->
<artifactId>spring-boot-starter-web</artifactId>

<!-- Jackson JSON -->
<artifactId>jackson-databind</artifactId>
```

---

## Statistics

- **Total Java Classes**: 11
- **Total Test Classes**: 2
- **Total Unit Tests**: 51 (all passing)
- **Lines of Code** (main): ~500
- **Lines of Code** (tests): ~600
- **API Endpoints**: 7
- **Status Types**: 4
- **Build Time**: ~30-45 seconds (first time with downloads)
- **Startup Time**: ~3-5 seconds
- **Test Execution Time**: ~15-20 seconds
- **Final JAR Size**: ~18MB
- **Docker Image Size**: ~250MB (multi-stage optimized)
- **MongoDB Image Size**: ~700MB
- **Docker Compose Total**: ~950MB on disk

---

## Future Enhancements

### Short Term (V1.1)
- [ ] User authentication (JWT tokens)
- [ ] User roles and permissions
- [ ] Todo priority levels (Low, Medium, High)
- [ ] Todo due dates and reminders
- [ ] Attachment support
- [ ] Comments/notes on todos
- [ ] Task categories/tags
- [ ] Recurring todos
- [ ] Performance metrics and logging
- [ ] API rate limiting

### Medium Term (V1.2)
- [ ] Real-time updates (WebSocket)
- [ ] Collaborative todos (share with others)
- [ ] Todo analytics and reporting
- [ ] Advanced search (Elasticsearch)
- [ ] Mobile app (React Native)
- [ ] Browser notifications
- [ ] Offline mode with sync
- [ ] Backup and restore functionality
- [ ] Email integration

### Long Term (V2.0)
- [ ] Machine learning for task prioritization
- [ ] AI-powered task suggestions
- [ ] Integration with calendar apps
- [ ] Microservices architecture
- [ ] Event-driven architecture (Kafka)
- [ ] GraphQL API option
- [ ] Advanced caching (Redis)
- [ ] Horizontal scaling
- [ ] Multi-language support
- [ ] Premium features and subscription model

---

## Verification Checklist

Run this checklist to verify the application is working correctly:

### Build Verification
- [ ] `mvn clean install` completes successfully
- [ ] All 51 tests pass
- [ ] JAR file created at `target/todoapp-api-1.0.0.jar`
- [ ] No compilation errors or warnings

### Application Startup
- [ ] `java -jar target/todoapp-api-1.0.0.jar` starts without errors
- [ ] Console shows "Tomcat started on port(s): 8080"
- [ ] Startup completes in ~3-4 seconds

### Frontend Access
- [ ] UI loads at http://localhost:8080
- [ ] Page displays properly (no CSS/JS errors)
- [ ] All buttons and form fields are visible

### API Endpoints
- [ ] `POST /api/todos` creates new todo (HTTP 201)
- [ ] `GET /api/todos` returns list (HTTP 200)
- [ ] `GET /api/todos/1` returns single todo (HTTP 200)
- [ ] `PUT /api/todos/1` updates todo (HTTP 200)
- [ ] `DELETE /api/todos/1` deletes todo (HTTP 204)
- [ ] `GET /api/todos?status=PENDING` filters todos (HTTP 200)
- [ ] `GET /api/todos?search=keyword` searches todos (HTTP 200)

### Error Handling
- [ ] `GET /api/todos/999` returns 404
- [ ] Invalid JSON returns 400
- [ ] CORS headers present in responses

### Docker
- [ ] `docker build -t todoapp:latest .` succeeds
- [ ] `docker run -d -p 8080:8080 todoapp:latest` starts container
- [ ] Container accessible at http://localhost:8080
- [ ] `docker-compose up --build` works

### Database
- [ ] H2 console accessible at http://localhost:8080/h2-console
- [ ] Sample data persists during application runtime
- [ ] Todos display in UI after creation

---

## Getting Help

### Common Questions

**Q: How do I change the port from 8080?**
A: Use the command: `java -jar target/todoapp-api-1.0.0.jar --server.port=9090`

**Q: Can I use PostgreSQL instead of H2?**
A: Yes, see "Database Configuration" section for step-by-step instructions.

**Q: How do I run tests?**
A: Use: `mvn test`

**Q: Is the frontend separated from the backend?**
A: Yes, but currently served by the same server. You can deploy them separately by serving `index.html` from a CDN.

**Q: Can I use this in production?**
A: Yes, but add authentication, restrict CORS, use persistent database, and enable HTTPS first.

**Q: How do I deploy to cloud?**
A: Build Docker image and push to Docker Hub, then deploy to AWS/GCP/Azure using their container services.

---

## License

This project is provided as-is for educational purposes.

---

## Support & Feedback

For issues, questions, or suggestions:
1. Check the Troubleshooting section
2. Review the API documentation
3. Check test files for usage examples
4. Review BDD scenarios for expected behavior

---

## Project Statistics

**Last Updated**: 2026-04-17

**Version**: 1.0.0

**Status**: Production Ready

**Test Coverage**: 51 tests covering all major scenarios

**Build Tool**: Maven 3.9.14

**Java Version**: 21

**Spring Boot Version**: 3.2.0

---

**End of Documentation**

This comprehensive README includes everything needed to understand, build, test, deploy, and extend the Todo Management Application. For any questions or clarifications, refer to the specific sections mentioned in the Table of Contents.
