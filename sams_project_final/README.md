# Simple Airline Management System (SAMS)

A Flask-based web application for managing airline operations, including flights, airplanes, airports, and more.

## Features

- User authentication and role management
- Airplane management
- Flight scheduling and tracking
- Airport management
- Database views and stored procedures
- Real-time system state display

## Prerequisites

- Python 3.6 or higher
- MySQL Server 8.0 or higher
- pip (Python package manager)

## Setup Instructions

1. Clone the repository
2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure MySQL:
- Create a new database named `flight_system`
- Import the database schema from `backend/schema.sql`
- Update database credentials in `.env` file

5. Set up environment variables:
Create a `.env` file with:
```
DB_HOST=localhost
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=flight_system
SECRET_KEY=your_secret_key
```

6. Run the application:
```bash
python app.py
```

The application will be available at http://localhost:5000

## Project Structure

```
sams_project_final/
├── app.py              # Main Flask application
├── backend/
│   ├── schema.sql     # Database schema
│   └── views/         # Database views
├── frontend/
│   └── templates/     # HTML templates
└── requirements.txt   # Python dependencies
```

## Technologies Used

- Backend: Flask (Python)
- Database: MySQL 8.0
- Frontend: HTML, Bootstrap, JavaScript
  We have basic HTML pages that allow users to interact with our backing database, powered by a Flash backend.

## Team Members

All team members worked equally on a combination of implementing procedures and views, frontend development, and debugging.
