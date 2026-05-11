# SWFLN Data Management System

## Overview

SWFLN (Southwest Florida Library Network) is a comprehensive web-based data management system designed to streamline the collection, processing, and analysis of library and community center data. The system allows users to upload data files from various sources, automatically processes them into a structured database, and provides intuitive dashboards and reports for insights into loans, events, tutorials, and user metrics.

## For Users: How to Use the System

### Getting Started
1. **Access the Application**: Open your web browser and navigate to the application's URL (provided by your administrator).
2. **Log In**: Use your username and password to log into the system. If you've forgotten your credentials, use the "Forgot Password" or "Forgot Username" features.

### Uploading Data
The system supports data uploads from three main sources:
- **LibCal**: Upload event registration and attendance data.
- **MyTurn**: Upload item loan/checkout data.
- **Niche**: Upload additional community program data.

To upload:
1. Navigate to the appropriate upload page (e.g., "Upload LibCal Data").
2. Select and upload your data file (typically CSV or Excel format).
3. The system will automatically process the file in the background.

### Viewing Data
- **Dashboard**: Get an overview of key metrics, recent uploads, and system status.
- **Reports**: Generate detailed reports on loans, events, tutorials, and user activity.
- **Roster**: View event attendance rosters and registrant lists.

### Account Management
- Update your profile information.
- Change your password.
- Contact administrators for role changes or access issues.

### What the System Expects
- **File Formats**: CSV or Excel files with specific column structures (refer to upload page instructions).
- **Data Quality**: Clean, consistent data without missing required fields.
- **User Roles**: Different access levels (admin, user) determine available features.

## For Developers: System Architecture and Flow

### Technology Stack
- **Backend**: FastAPI (Python) with SQLAlchemy ORM
- **Database**: PostgreSQL (hosted on Supabase)
- **Frontend**: Vanilla JavaScript, HTML, CSS (no frameworks)
- **Authentication**: Session-based with password hashing
- **File Processing**: Asynchronous ingestion and transformation
- **Email**: SMTP integration for notifications
- **Deployment**: Cloud deployment on Render

### End-to-End Flow

1. **User Authentication**:
   - User submits login credentials via frontend form.
   - Backend validates against database (users table).
   - Session token created and stored in database.
   - Frontend receives token for subsequent requests.

2. **File Upload**:
   - User selects file and submits via upload form.
   - Frontend sends file to backend API endpoint.
   - Backend stores file temporarily and creates uploaded_files record.
   - Asynchronous processing begins.

3. **Data Ingestion**:
   - Background job processes uploaded file based on source type.
   - Raw data parsed and validated using source-specific schemas.
   - Data transformed into normalized database records (items, loans, events, etc.).

4. **Data Storage**:
   - Processed data inserted into PostgreSQL tables.
   - Relationships maintained via foreign keys.
   - Status updated in uploaded_files table.

5. **Data Retrieval**:
   - Frontend makes API calls to retrieve processed data.
   - Backend queries database using SQLAlchemy models.
   - Data returned as JSON for frontend rendering.

6. **Reporting and Analytics**:
   - Admin routes provide aggregated data queries.
   - Frontend visualizes data in tables, charts, and reports.
   - Export functionality generates downloadable reports.

### Key Components

#### Backend Structure
- `app.py`: Main FastAPI application setup, CORS, static file serving.
- `routes/`: API endpoints for auth and admin functions.
- `models/`: SQLAlchemy ORM models for database tables.
- `services.py`: Business logic for data processing.
- `queries.py`: Database query functions.
- `validators.py`: Input validation logic.
- `email_service.py`: Email notification handling.
- `scripts/`: Database maintenance and setup scripts.

#### Database Schema
- **users**: User accounts and authentication.
- **uploaded_files**: Metadata for uploaded data files.
- **items**: Catalog items available for loan.
- **loans**: Loan/checkout transactions.
- **events**: Event registrations and attendance.
- **tutorials**: Tutorial content and metrics.
- **registrants**: Event registrant details.

#### Frontend Structure
- `index.html`: Main application shell.
- `pages/`: Individual page templates.
- `src/`: JavaScript modules for API calls, components, and utilities.
- `styles/`: CSS for styling.

### Development Setup
1. Clone the repository.
2. Set up Python virtual environment.
3. Install dependencies: `pip install -r backend/requirements.txt`.
4. Configure environment variables (.env file).
5. Run database migrations: `python backend/scripts/create_tables.py`.
6. Start the server: `uvicorn backend.app:app --reload`.
7. Access frontend at `http://localhost:8000/frontend`.

### API Endpoints
- `POST /auth/login`: User authentication.
- `POST /auth/register`: User registration.
- `POST /admin/upload`: File upload.
- `GET /admin/dashboard`: Dashboard data.
- `GET /admin/reports`: Report generation.

### Security Considerations
- Password hashing using secure algorithms.
- Session management with expiration.
- CORS configuration for frontend access.
- Input validation and sanitization.
- Role-based access control.

## Developer Contact Information

- **Backend Developer**: Nelson Rengifo, nrengifo3107@gmail.com
- **Frontend Developer**: Jared Margarito, jmargarito2015@gmail.com