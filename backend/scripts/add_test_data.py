from pymongo import MongoClient
from datetime import datetime, timedelta
import random

client = MongoClient('mongodb://localhost:27017')
db = client.crimespot

# Chennai boundaries
LAT_MIN, LAT_MAX = 13.0, 13.2
LON_MIN, LON_MAX = 80.2, 80.3

# Sample crime types
CRIME_TYPES = ['theft', 'assault', 'robbery', 'vandalism']

# Generate 50 sample reports
sample_reports = []
now = datetime.utcnow()

for _ in range(50):
    lat = random.uniform(LAT_MIN, LAT_MAX)
    lon = random.uniform(LON_MIN, LON_MAX)
    
    report = {
        "crime_type": random.choice(CRIME_TYPES),
        "location": {
            "type": "Point",
            "coordinates": [lon, lat]  # MongoDB uses [longitude, latitude]
        },
        "date_time": now - timedelta(days=random.randint(0, 30)),
        "description": "Sample crime report"
    }
    sample_reports.append(report)

# Create geospatial index
db.crime_reports.create_index([("location", "2dsphere")])

# Insert sample data
db.crime_reports.insert_many(sample_reports)
print(f"Added {len(sample_reports)} sample reports")