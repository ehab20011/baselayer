# PPP Loan Data API

A FastAPI-based application that scrapes, processes, and serves PPP (Paycheck Protection Program) loan data through a REST API. The application automatically downloads data from the SBA website, processes it, and stores it in a PostgreSQL database.

## Features

- 🤖 Automated web scraping of PPP loan data from SBA website
- 🧹 Comprehensive data cleaning and validation
- 📊 PostgreSQL database with optimized indexes
- 🚀 FastAPI REST endpoints
- 🐳 Fully containerized with Docker

## Quick Start

### Prerequisites
- Docker
- Docker Compose

### Running the Application

1. Clone this repository:
```bash
git clone <https://github.com/ehab20011/baselayer.git>
cd BaseLayer
```

2. Start the application:
```bash
docker-compose up --build
```

That's it! The application will:
- Start PostgreSQL database
- Download PPP loan data
- Clean and load the data (limited to 5000 rows)
- Start the FastAPI server

### Accessing the API

Once running, you can access:
- API endpoints: http://localhost:8000
- Interactive API documentation: http://localhost:8000/docs
- OpenAPI specification: http://localhost:8000/openapi.json

## Application Components

### 1. Data Scraping (`scraper.py`)
- Uses Playwright to automatically navigate and download PPP data
- Handles authentication and file downloads
- Manages browser automation with proper error handling

### 2. Data Processing (`send_to_postgres.py`)
- Cleans and validates PPP loan data
- Processes data in efficient batches
- Handles data type conversion and standardization
- Manages database connections and transactions

### 3. API Server (`api.py`)
- FastAPI-based REST endpoints
- Serves PPP loan data with various query parameters
- Optimized database queries with proper indexing

### 4. Database Schema (`init.sql`)
- PostgreSQL database initialization
- Table definitions and constraints
- Index creation for optimized queries

## Data Cleaning

The application performs extensive data cleaning:
- Standardizes null values
- Rounds numeric fields to 2 decimal places
- Handles multiple date formats
- Cleans and standardizes string fields
- Processes boolean fields consistently

## Docker Configuration

The application uses two Docker containers:
1. **API Container**:
   - Python 3.9
   - FastAPI
   - Playwright for web scraping
   - Chrome browser for automation

2. **Database Container**:
   - PostgreSQL 13
   - Persistent data storage
   - Automatic initialization
   - Health checks

### Environment Variables

Default values are provided in `docker-compose.yml`, but can be overridden with a `.env` file:
```env
DATABASE_URL=postgresql://postgres:Baselayerproject123@db:5432/ppp_database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=Baselayerproject123
POSTGRES_DB=ppp_database
```

## Maintenance Commands

```bash
# View logs
docker-compose logs

# Stop the application
docker-compose down

# Reset everything (including database)
docker-compose down -v

# Rebuild containers
docker-compose up --build
```

## Data Persistence

- Database data persists in the `ppp_loans_data` volume
- Data survives container restarts
- Use `docker-compose down -v` to reset data

## Troubleshooting

1. **Database Connection Issues**
   - Check if PostgreSQL container is healthy:
     ```bash
     docker-compose logs db
     ```
   - The API will automatically wait for database availability

2. **Scraping Issues**
   - Check Chrome/Playwright logs:
     ```bash
     docker-compose logs api
     ```
   - Ensure internet connectivity

3. **Performance Issues**
   - Database is indexed for common queries
   - Data is loaded in batches
   - Container resources can be adjusted in docker-compose.yml

## API Endpoints

The API provides several endpoints for querying PPP loan data:
- GET `/business/{loan_number}`: Retrieve specific loan details
- GET `/businesses`: List all businesses with pagination
- Additional endpoints documented in the Swagger UI

## Security Notes

- Database credentials are managed through environment variables
- API runs on localhost by default
- No sensitive data is exposed in logs
- All external dependencies are version-locked

## Development

To modify or extend the application:
1. Make changes to the relevant Python files
2. Rebuild containers: `docker-compose up --build`
3. Check logs for any issues: `docker-compose logs`

The application is designed to be easily extensible for additional features or data processing requirements.
