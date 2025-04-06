# Call Analysis System Backend

This is the backend API for the Call Analysis System, built with FastAPI.

## Features

- CSV file upload and analysis
- Call data analysis by shift and resource allocation
- RESTful API for frontend integration

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the server:
   ```bash
   python run.py
   ```

   The API will be available at http://localhost:8000

4. API Documentation:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

- `GET /`: API root - welcome message
- `POST /api/analysis/upload-and-analyze`: Upload and analyze a CSV file
- `GET /api/analysis/results/{file_id}`: Get results for a specific file
- `GET /api/analysis/sample-data`: Get sample data for development

## Deployment

For deployment to Render.com or similar services, configure the service to:

1. Install dependencies from requirements.txt
2. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT` 