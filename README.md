# **ODK Pipeline Ingestion API**

## **Overview**

This API is designed to receive, store, and retrieve ODK (Open Data Kit) submissions for the Unlock System. It supports structured data formats (**JSON, XML**) and geospatial data (**WKT/GeoJSON**) using **FastAPI** and **PostgreSQL with PostGIS**.

## **Features**

Accepts ODK submissions via a REST API.  
Stores structured data (**JSON, XML**) and geospatial data (**WKT/GeoJSON**).  
Enforces **unique constraints** on `odk_id` to prevent duplicate submissions.  
Validates and rejects **invalid geolocation data**.  
Ensures **empty `odk_id` values are not accepted**.  
Supports **high-concurrency data ingestion** without failures.  
Provides API endpoints to retrieve stored submissions.  
Uses **PostgreSQL with PostGIS** for efficient geospatial storage.  
Supports **Swagger UI** for API testing.

## **Installation & Setup**

### **Clone the Repository**

```sh
git clone https://github.com/islas104/pipeline-ingestion-api.git
cd pipeline-ingestion-api
```

### Create a Virtual Environment

```sh
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

### Install Dependencies

```sh
pip install -r requirements.txt
```

### Running the API

**Start the Server**

```sh
uvicorn src.main:app --reload
```

The API will be available at:
➡️ http://127.0.0.1:8000

### **Database Setup & Migrations**

Before running the API, apply the database migrations:

```sh
alembic upgrade head
```
