# Data Connection Configuration for ESR Orchestrator Testing

## 🏗️ How to Connect Your Data

### 1. **Database Connection** (Recommended for production)

Update `src/tools/waste_tracking.py` to connect to your database:

```python
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

# Example for PostgreSQL/MySQL
DATABASE_URL = "postgresql://user:password@localhost/esr_db"
# or: "mysql+pymysql://user:password@localhost/esr_db"

engine = sa.create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def get_waste_info_from_db(selector: str) -> dict:
    with Session() as session:
        # Example query - adjust to your schema
        query = """
        SELECT batch_id, container_id, material, quantity_kg, 
               location, storage_start, handler
        FROM waste_containers 
        WHERE container_id = :selector OR batch_id = :selector
        """
        result = session.execute(sa.text(query), {"selector": selector})
        rows = result.fetchall()
        return {"results": [dict(row) for row in rows]}
```

### 2. **REST API Integration**

Update `src/tools/insurer_api.py` for your real insurer API:

```python
# Your actual insurer API configuration
INSURER_CONFIG = {
    "base_url": "https://api.yourinsurer.com/v2",
    "auth_token": "your-api-token",  # From .env
    "endpoints": {
        "claims": "/claims",
        "policies": "/policies",
        "coverage": "/coverage-check"
    }
}

async def submit_claim(claim_data: dict) -> dict:
    url = f"{INSURER_CONFIG['base_url']}{INSURER_CONFIG['endpoints']['claims']}"
    headers = {
        "Authorization": f"Bearer {INSURER_CONFIG['auth_token']}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=claim_data, headers=headers)
        return response.json()
```

### 3. **File-based Data Sources**

For CSV/Excel files, update the data directory:

```bash
# Add your real data files to:
data/
├── waste_inventory.csv          # Your current waste data
├── compliance_records.xlsx      # Compliance history
├── insurance_policies.json      # Policy details
├── regulations/
│   ├── local_regulations.pdf    # Local environmental rules
│   └── industry_standards.txt   # Industry-specific standards
└── incidents/
    ├── 2024_incidents.csv       # Historical incidents
    └── claims_history.json      # Insurance claims data
```

### 4. **Real-time Sensor Data**

For IoT/sensor integration, add to `src/tools/`:

```python
# src/tools/sensor_monitoring.py
import asyncio
from datetime import datetime

async def get_sensor_data(container_id: str) -> dict:
    # Example: Connect to your sensor API
    sensor_api = "https://sensors.yourcompany.com/api/v1"
    
    # Real-time temperature, humidity, leak detection
    return {
        "container_id": container_id,
        "timestamp": datetime.now().isoformat(),
        "temperature": 23.5,  # Celsius
        "humidity": 45.2,     # Percentage
        "leak_detected": False,
        "gas_levels": {"CO2": 400, "O2": 20.9}
    }
```

## 🧪 Testing Your Data Connections

### Quick Test Commands:

```bash
# 1. Start the server
uvicorn src.app:app --reload --port 8010

# 2. Run test scenarios
python test_scenarios.py

# 3. Test specific scenario
python test_scenarios.py "Battery Leak Incident"

# 4. Test with your real data
curl -X POST http://localhost:8010/run \
  -H "Content-Type: application/json" \
  -d '{"task":"Check compliance status for container [YOUR_CONTAINER_ID]"}'
```

### Environment Variables to Set:

```bash
# Copy .env.example to .env and add:
OPENAI_API_KEY=your-openai-key
DATABASE_URL=your-database-connection-string
INSURER_API_BASE=https://api.yourinsurer.com
INSURER_API_TOKEN=your-insurer-api-token
SENSOR_API_BASE=https://sensors.yourcompany.com
```

## 📊 Data Schema Requirements

Your data should include these key fields:

### Waste Data:
- `container_id` (unique identifier)
- `material` (waste type)
- `quantity_kg` (amount)
- `location` (storage site)
- `storage_start` (date)
- `handler` (responsible party)

### Compliance Data:
- `regulation_id` (standard reference)
- `requirement` (what's required)
- `status` (compliant/non-compliant)
- `last_check` (inspection date)

### Insurance Data:
- `policy_number`
- `coverage_type`
- `coverage_amount`
- `deductible`
- `expiry_date`

## 🔧 Next Steps

1. **Choose your data source** (database, API, files)
2. **Update connection settings** in `.env`
3. **Modify the relevant tool files** (waste_tracking.py, insurer_api.py)
4. **Test with real data** using the test scenarios
5. **Use LangGraph Studio** for visual debugging

Need help with any specific data connection? Let me know your data source type and I'll provide detailed integration code!
