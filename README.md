# OnDutyService — ระบบจัดการเวรรักษาการณ์

A web application for organizing officers on duty each month and managing duty-exchange requests.

## Tech Stack

| Layer    | Technology            |
|----------|-----------------------|
| Frontend | Vue.js 3 + Vite       |
| Backend  | Python 3.11 + FastAPI |
| Database | MongoDB 7             |

## Features

- **Officer Management** — Add, edit, and remove officers with rank and badge information.
- **Monthly Duty Schedule** — Create and view a calendar-based duty roster for each month.
- **Duty Exchange Requests** — Officers can request to swap duty days; admins can approve or reject requests. Approved swaps are automatically reflected in the schedule.

## Project Structure

```
OnDutyService/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── main.py       # Application entry point
│   │   ├── config.py     # Settings (env vars)
│   │   ├── database.py   # MongoDB connection
│   │   ├── models/       # Pydantic models
│   │   └── routes/       # API route handlers
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/             # Vue.js application
│   ├── src/
│   │   ├── views/        # Page components
│   │   ├── services/     # Axios API client
│   │   ├── router/       # Vue Router config
│   │   └── main.js
│   ├── Dockerfile
│   └── nginx.conf
└── docker-compose.yml
```

## Quick Start with Docker Compose

```bash
docker compose up --build
```

- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Docs (Swagger): http://localhost:8000/docs

## Local Development

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env            # Edit MONGODB_URL if needed
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local      # Edit VITE_API_URL if needed
npm run dev
```

## API Endpoints

| Method | Path                        | Description                  |
|--------|-----------------------------|------------------------------|
| GET    | /api/officers/              | List all officers            |
| POST   | /api/officers/              | Create an officer            |
| PUT    | /api/officers/{id}          | Update an officer            |
| DELETE | /api/officers/{id}          | Delete an officer            |
| GET    | /api/schedules/{year}/{mon} | Get monthly schedule         |
| POST   | /api/schedules/             | Create a monthly schedule    |
| PUT    | /api/schedules/{year}/{mon} | Update schedule entries      |
| GET    | /api/exchanges/             | List exchange requests       |
| POST   | /api/exchanges/             | Create an exchange request   |
| PUT    | /api/exchanges/{id}         | Approve / reject a request   |

