# FastAPI Backend

This repository contains the FastAPI backend for the Artisan project—a full‑stack application designed to manage leads. The backend supports CRUD operations, filtering, sorting, CSV export, JWT authentication, and real‑time updates via WebSockets.This uses SQLAlchemy (with asyncpg) for asynchronous interactions with a PostgreSQL database. It is containerized using Docker and deployed on AWS Elastic Beanstalk with an AWS RDS PostgreSQL instance.

## URL
Try the React -App: https://main.d3v82t4zx92fjf.amplifyapp.com/

Backend API Endpoint: https://api.backenddemo.site/docs#/

## Features

- **CRUD Operations:** Create, read, update, and delete leads.
- **Advanced Querying:** Filtering, sorting, and pagination.
- **CSV Export:** Export lead data as CSV.
- **JWT Authentication:** Secure authentication and authorization.
- **Real‑time Updates:** WebSocket integration for live updates.
- **Containerized Deployment:** Docker support for easy deployment.

## Technologies

- **Framework:** FastAPI
- **ORM:** SQLAlchemy with asyncpg
- **Migrations:** Alembic
- **Real-time:** WebSockets
- **Authentication:** JWT (using jose and passlib)
- **Containerization:** Docker
- **Cloud:** AWS Elastic Beanstalk, AWS RDS

## Demo:
https://www.loom.com/share/7220a5aa11fc4c708f835401da0288a2?sid=453e5a51-2275-4103-844e-5257bb92c543

## Local Setup & Installation

### Prerequisites

- Python 3.12 or higher
- PostgreSQL (local instance or remote)
- Git
- Docker (optional, for container testing)

### Steps

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/artisan-backend.git
   cd artisan-backend

2. **Create a Virtual Environment:**

   ```bash
   python -m venv venv
* On Windows:
  ```bash
  venv\Scripts\activate
* On macOS/Linux:
```bash
  source venv/bin/activate 
 ```
3. **Install Dependencies:**
   ```bash
    pip install --upgrade pip
    pip install -r requirements.txt

4. **Configure Environment Variables:**
  Create a .env file in the project root with the following contents:
 ```bash
    DATABASE_URL=postgresql+asyncpg://<db_user>:<db_password>@<db_host>:5432/<db_name>
    JWT_SECRET_KEY=your_super_secret_key
    JWT_ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=120
  ```
5.  **Database Migrations:**
   * Generate a New Migration:
    ```bash
      alembic revision --autogenerate -m "Creating DB tables"
    ```
   * Apply the Migrations:
     ```bash
      alembic upgrade head
     ```
7. **Running the Application:**
   ```bash
     uvicorn app.main:app --reload --log-level debug
   ```
