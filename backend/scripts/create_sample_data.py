import asyncio
from datetime import datetime, timedelta
import random
from database import Database
from models.database_models import CrimeReportDB

# Chennai area boundaries (approximately)
CHENNAI_BOUNDS = {
    'min_lat': 12.8,
    'max_lat': 13.2,
    'min_lng': 80.1,
    'max_lng': 80.4
}

CRIME_TYPES = [
    'Theft', 'Burglary', 'Assault', 'Fraud', 
    'Cybercrime', 'Robbery', 'Harassment'
]

SEVERITY_LEVELS = ['Low', 'Medium', 'High', 'Critical']
STATUS_OPTIONS = ['Open', 'Investigating', 'Pending', 'Closed']

OFFICERS = [
    {'name': 'Officer Priya', 'badge': 'TNPD-691'},
    {'name': 'Officer Raj', 'badge': 'TNPD-445'},
    {'name': 'Officer Kumar', 'badge': 'TNPD-223'},
    {'name': 'Officer Lakshmi', 'badge': 'TNPD-867'}
]

EVIDENCE_TYPES = [
    'DNA Sample', 'Weapon Found', 'CCTV Footage',
    'Fingerprints', 'Documents', 'Digital Evidence',
    'Photographs', 'Audio Recording', 'Witness Statement'
]

TAGS = [
    'violence', 'cyber', 'organized_crime', 'property',
    'financial', 'public_safety', 'traffic', 'drugs',
    'domestic', 'white_collar'
]

SAMPLE_DESCRIPTIONS = [
    "Online scam reported involving cryptocurrency",
    "Credit card fraud at local ATM",
    "Identity theft case reported",
    "Cyberbullying incident on social media",
    "Bank account hacking attempt",
    "Phishing email campaign detected",
    "Mobile wallet fraud reported"
]

def generate_crime_id():
    return f"CID_{str(random.randint(1, 999)).zfill(3)}"

async def create_sample_reports(num_reports=100):
    await Database.connect()
    
    try:
        for _ in range(num_reports):
            # Generate random location within Chennai
            lat = random.uniform(CHENNAI_BOUNDS['min_lat'], CHENNAI_BOUNDS['max_lat'])
            lng = random.uniform(CHENNAI_BOUNDS['min_lng'], CHENNAI_BOUNDS['max_lng'])
            
            # Random date within next 2 years (for demonstration)
            days_ahead = random.randint(-30, 730)  # Between 30 days ago and 2 years ahead
            random_date = datetime.utcnow() + timedelta(days=days_ahead)
            
            # Random evidence (2-4 items)
            evidence_count = random.randint(2, 4)
            evidence = random.sample(EVIDENCE_TYPES, evidence_count)
            
            # Random tags (2-4 items)
            tag_count = random.randint(2, 4)
            tags = random.sample(TAGS, tag_count)
            
            report = {
                "crime_id": generate_crime_id(),
                "timestamp": random_date,
                "location": {
                    "type": "Point",
                    "coordinates": [lng, lat]
                },
                "crime_type": random.choice(CRIME_TYPES),
                "description": random.choice(SAMPLE_DESCRIPTIONS),
                "severity": random.choice(SEVERITY_LEVELS),
                "status": random.choice(STATUS_OPTIONS),
                "officer_in_charge": random.choice(OFFICERS),
                "witnesses": [],  # Empty array as per sample
                "evidence": evidence,
                "tags": tags
            }
            
            report_id = await CrimeReportDB.create(report)
            print(f"Created report {report['crime_id']} of type {report['crime_type']}")
            
    finally:
        await Database.close()

if __name__ == "__main__":
    print("Creating sample crime reports...")
    asyncio.run(create_sample_reports())
    print("Sample data creation completed!")
