# Task Management Application

A lightweight task management application built with Flask (backend), React (frontend), and Docker.

## Features

- Create tasks with titles
- Mark tasks as completed
- Delete tasks
- View statistics (total, completed, pending tasks)
- Responsive design
- Dockerized for easy deployment

## Getting Started

### Run with Docker Compose

1. Clone the repository:
```bash
git clone <repository-url>
cd carbonarc
```

2. Build and run the application:
```bash
docker-compose up --build
```

3. Access the application:
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:5000

### Stop the application:
```bash
docker-compose down
```

## API Documentation

The backend exposes the following REST API endpoints:

### 1. List All Tasks
```bash
curl http://localhost:5000/tasks
```
**Response:**
```json
[
  {
    "id": 1,
    "title": "Write report",
    "completed": false
  }
]
```

### 2. Create a Task
```bash
curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Write report"}'
```
**Response:**
```json
{
  "id": 1,
  "title": "Write report",
  "completed": false
}
```

### 3. Mark Task as Complete
```bash
curl -X PUT http://localhost:5000/tasks/1/complete
```
**Response:**
```json
{
  "id": 1,
  "title": "Write report",
  "completed": true
}
```

### 4. Delete a Task
```bash
curl -X DELETE http://localhost:5000/tasks/1
```
**Response:**
```json
{
  "id": 1,
  "title": "Write report",
  "completed": false
}
```

### 5. Get Statistics
```bash
curl http://localhost:5000/tasks/stats
```
**Response:**
```json
{
  "total": 5,
  "completed": 2,
  "pending": 3
}
```

## Development

### Backend Development

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the Flask app:
```bash
python app.py
```

Backend will run on http://localhost:5000

### Frontend Development

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm start
```

Frontend will run on http://localhost:3000

## Testing

### Backend Tests (pytest)

The backend includes a comprehensive test suite.

#### Running Tests Locally

```bash
cd backend
pip install -r requirements.txt
pytest
```

#### Run Specific Test File

```bash
pytest tests/test_api.py -v
pytest tests/test_models.py -v
pytest tests/test_integration.py -v
```

#### Running Tests in Docker

```bash
docker-compose run backend pytest
```

### Test Structure

- `tests/test_api.py` - API endpoint tests (GET, POST, PUT, DELETE, stats)
- `tests/test_models.py` - Pydantic model validation tests
- `tests/test_integration.py` - Integration workflow tests
- `tests/conftest.py` - pytest fixtures and configuration

## Notes

- **In-Memory Storage**: Tasks are stored in memory and will be lost when the backend container restarts
- **CORS**: Enabled for frontend-backend communication
- **Ports**: Backend uses port 5000, Frontend uses port 3000.

# Assumptions
I've assumed that tasks can have identical titles, that "completing" a completed task should succeed (with a 200) and do nothing, and that titles for tasks have an arbitrary limit of 200 characters, though this could be changed to pull some limit variable from the environment.

# Answers to questions
1. How did you handle API errors?
    Just by returning the proper code at the endpoint and continuing to serve requests, but I used Pydantic to handle some of the additional logic.

2. What tests would you write if given more time?
    I think that I was pretty thorough with my tests for the backend, but I don't have any tests in place for the frontend.

3. What would you improve with 1 extra hour?
    I would definitely start looking into data durability, since I still keep the tasks in memory. I was going to use PostGres but I ran out of time.