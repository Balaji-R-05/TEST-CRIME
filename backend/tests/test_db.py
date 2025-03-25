import asyncio
import sys
import os
from dotenv import load_dotenv
import pytest
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

from database import Database
from models.database_models import CrimeReportDB
from auth import get_password_hash, create_access_token, verify_password

async def test_database_connection():
    """Test basic database connection"""
    try:
        await Database.connect()
        assert Database.db is not None
        logger.info("Database connection successful")
    finally:
        await Database.close()

async def test_create_and_get_report():
    """Test creating and retrieving a crime report"""
    await Database.connect()
    try:
        # Test report data
        test_report = {
            "crime_type": "theft",
            "location": {
                "type": "Point",
                "coordinates": [80.2707, 13.0827],
                "address": "Test location"
            },
            "description": "Test crime report",
            "date_time": datetime.utcnow(),
            "is_anonymous": False,
            "status": "pending"
        }
        
        # Create report
        report_id = await CrimeReportDB.create(test_report)
        assert report_id is not None
        logger.info(f"Created report with ID: {report_id}")
        
        # Get report
        report = await CrimeReportDB.get_by_id(report_id)
        assert report is not None
        assert report["crime_type"] == "theft"
        logger.info("Successfully retrieved report")
        
    finally:
        await Database.close()

async def test_nearby_reports():
    """Test getting nearby reports"""
    await Database.connect()
    try:
        # Create multiple test reports
        reports = []
        for i in range(3):
            test_report = {
                "crime_type": "theft",
                "location": {
                    "type": "Point",
                    "coordinates": [80.2707 + (i * 0.001), 13.0827 + (i * 0.001)],
                    "address": f"Test location {i}"
                },
                "description": f"Test crime report {i}",
                "date_time": datetime.utcnow(),
                "is_anonymous": False,
                "status": "pending"
            }
            report_id = await CrimeReportDB.create(test_report)
            reports.append(report_id)
        
        # Test nearby search
        nearby = await CrimeReportDB.get_nearby(80.2707, 13.0827, 5000)
        assert len(nearby) > 0
        logger.info(f"Found {len(nearby)} nearby reports")
        
    finally:
        await Database.close()

async def test_user_auth():
    """Test user authentication functions"""
    await Database.connect()
    try:
        # Test user data
        test_user = {
            "username": "testuser",
            "email": "test@example.com",
            "hashed_password": get_password_hash("testpass123"),
            "full_name": "Test User",
            "disabled": False
        }
        
        # Create test user
        result = await Database.db.users.insert_one(test_user)
        user_id = str(result.inserted_id)
        assert user_id is not None
        
        # Test password verification
        assert verify_password("testpass123", test_user["hashed_password"])
        
        # Test token creation
        token = create_access_token({"sub": test_user["username"]})
        assert token is not None
        
        # Cleanup
        await Database.db.users.delete_one({"_id": result.inserted_id})
        
    finally:
        await Database.close()

def run_tests():
    """Run all tests"""
    logger.info("Starting tests...")
    
    asyncio.run(test_database_connection())
    logger.info("Database connection test completed")
    
    asyncio.run(test_create_and_get_report())
    logger.info("Crime report creation/retrieval test completed")
    
    asyncio.run(test_nearby_reports())
    logger.info("Nearby reports test completed")
    
    asyncio.run(test_user_auth())
    logger.info("User authentication test completed")
    
    logger.info("All tests completed successfully")

if __name__ == "__main__":
    run_tests()

