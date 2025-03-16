# PPP Loan Data Analytics Platform - Base Layer

A full-stack web application that provides analytics and visualization of PPP (Paycheck Protection Program) loan data. The platform combines automated data collection, backend processing, and an interactive frontend interface to showcase the PPP loan distributions.

![PPP](https://github.com/user-attachments/assets/87b2f054-01ac-4e96-bdc1-27dd73e6bc78)


## 🌟 Features

- Automated data collection from SBA website using Playwright
- Advanced data processing and validation pipeline
- PostgreSQL database with optimized query performance
- FastAPI-powered REST API
- Modern, responsive frontend interface
- Complete Docker containerization
- Comprehensive test coverage
- Real-time data visualization

## 🏗 Architecture

The application follows a modern three-tier architecture:

### Backend Components
1. **Data Collection (`scraper.py`)**
   - Automated web scraping using Playwright
   - Secure authentication handling
   - Robust error handling and retry mechanisms
   - Configurable download parameters

2. **Data Processing (`send_to_postgres.py`)**
   - ETL pipeline for raw PPP data
   - Data validation and cleaning
   - Efficient batch processing
   - Type conversion and standardization

3. **API Layer (`api.py`)**
   - RESTful endpoints using FastAPI
   - Async request handling
   - Comprehensive data filtering
   - Pagination support
   - OpenAPI documentation

4. **Database (`init.sql`, `create_indexes.py`)**
   - PostgreSQL 13 database
   - Optimized table schemas
   - Strategic indexing
   - Data integrity constraints

### Frontend Components (`frontend/`)
- Modern HTML5/CSS3/JavaScript stack
- Responsive design
- Interactive data visualizations
- Real-time data updates
- Cross-browser compatibility

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git
- 4GB+ RAM recommended

### Installation

1. Clone the repository:
```bash
git clone https://github.com/ehab20011/baselayer.git
cd baselayer
```

2. Start the application:
```bash
docker-compose up --build
```
If this doesnt work try:
```bash
docker-compose down -v
docker-compose up --build
```

The platform will automatically:
- Initialize the PostgreSQL database
- Run database migrations
- Start data collection
- Launch the API server
- Serve the frontend application

### Access Points
- Frontend Interface: http://localhost:3000
- API Documentation: http://localhost:8000/docs
- OpenAPI Spec: http://localhost:8000/openapi.json

## 🔧 Configuration

### Docker Configuration
- `docker-compose.yml`: Container orchestration
- `Dockerfile`: API service configuration
- Volume mapping for persistent data

## 📊 Data Model

### Core Tables
1. **PPP Loans**
   - Loan details
   - Business information
   - Amount and status
   - Temporal data

2. **Businesses**
   - Company information
   - Industry classification
   - Location data
   - Employee counts

### Indexes
- Optimized for common queries
- Full-text search capabilities
- Geospatial indexing

## 🔌 API Endpoints

### Business Operations
- `GET /business/{loan_number}`: Detailed loan information
- `GET /businesses`: Paginated business listing
- `GET /businesses/search`: Full-text search
- `GET /businesses/stats`: Aggregated statistics

### Analytics
- `GET /analytics/industry`: Industry-wise distribution
- `GET /analytics/temporal`: Time-series analysis
- `GET /analytics/geographic`: Geographic distribution

## 🧪 Testing

The project includes comprehensive testing:

```bash
# Run all tests
python -m pytest

# Run specific test categories
python -m pytest tests/test_api.py
python -m pytest tests/test_processing.py
```

## 🛠 Development

### Local Setup
1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run development server:
```bash
uvicorn api:app --reload
```

### Code Structure
```
baselayer/
├── api.py           # FastAPI application
├── models.py        # Data models
├── scraper.py       # Data collection
├── send_to_postgres.py  # Data processing
├── init_service.py  # Initialization
├── create_indexes.py    # Database optimization
├── frontend/        # Web interface
│   ├── index.html
│   ├── script.js
│   └── styles.css
└── tests/           # Test suite
```

## 📈 Performance

- Connection pooling
- Query optimization
- Batch processing
- Caching strategies
- Load balancing ready

## 🔍 Troubleshooting

### Common Issues
1. **Database Connection**
   ```bash
   docker-compose logs db
   ```

2. **Data Collection**
   ```bash
   docker-compose logs api
   ```

3. **Performance**
   - Check resource allocation
   - Monitor query performance
   - Review connection pools
