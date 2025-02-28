**ODK Pipeline Ingestion API**

**Overview**

This API is designed to receive, store, and retrieve ODK (Open Data Kit) submissions for the Unlock System. It supports structured data formats (JSON, XML) and geospatial data (WKT/GeoJSON) using FastAPI and PostgreSQL with PostGIS.

**Features**

- Accepts ODK submissions via a REST API.
- Stores structured data (JSON, XML).
- Handles geospatial data (WKT/GeoJSON).
- Provides API endpoints to retrieve stored submissions.
- Uses PostgreSQL (with PostGIS) for efficient geospatial storage.

**Installation & Setup**

**Clone the Repository**

git clone https://github.com/islas104/pipeline-ingestion-api.git

cd pipeline-ingestion-api

**Create a Virtual Environment**

python3 -m venv venv

source venv/bin/activate # Mac/Linux

venv\Scripts\activate # Windows

**Install Dependencies**

pip install -r requirements.txt

**Setup PostgreSQL & PostGIS**

Ensure PostgreSQL and PostGIS are installed. Then, create the database:

psql -U postgres -c "CREATE DATABASE pipeline_ingestion;"

psql -U postgres -d pipeline_ingestion -c "CREATE EXTENSION postgis;"

Create the submissions table:

CREATE TABLE submissions (

id SERIAL PRIMARY KEY,

odk_id TEXT NOT NULL,

data JSONB NOT NULL,

geolocation GEOMETRY(Point, 4326)

);

**Running the API**

**Start the Server**

uvicorn main:app --reload

The API will be available at:\
<http://127.0.0.1:8000>

**Swagger UI Documentation**

Visit http://127.0.0.1:8000/docs to test the API via Swagger UI.

**API Endpoints**

**Submit Data (POST)**

**Endpoint:**

POST /submissions/

**Request Body (JSON Example)**

{

"odk_id": "test123",

"data": {"question1": "yes", "question2": "no"},

"geolocation": "POINT(-0.127758 51.507351)"

}

**Response:**

{

"id": 1,

"odk_id": "test123",

"data": {"question1": "yes", "question2": "no"},

"geolocation": "POINT(-0.127758 51.507351)"

}

**Retrieve Submission by ID (GET)**

**Endpoint:**

GET /submissions/{id}

**Example:**

curl -X 'GET' 'http://127.0.0.1:8000/submissions/1'

**Response:**

{

"id": 1,

"odk_id": "test123",

"data": {"question1": "yes", "question2": "no"},

"geolocation": "POINT(-0.127758 51.507351)"

}

**Resetting the Database (For Testing)**

If you need to clear all data:

psql -U postgres -d pipeline_ingestion -c "TRUNCATE TABLE submissions RESTART IDENTITY CASCADE;"

**Troubleshooting**

**PostgreSQL Connection Issues**

Make sure your PostgreSQL server is running and listening on the correct port.

Check connection:

psql -U postgres -d pipeline_ingestion

**Uvicorn Fails to Start**

Ensure the database is set up and dependencies are installed:

pip install -r requirements.txt

**Author**

Developed by Islas Ahmed Nawaz
