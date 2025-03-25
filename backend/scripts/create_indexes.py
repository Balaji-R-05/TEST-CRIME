from database import Database
import asyncio

async def create_indexes():
    await Database.connect()
    
    try:
        # Create indexes for crime reports
        await Database.db.crime_reports.create_index([("location", "2dsphere")])
        await Database.db.crime_reports.create_index("timestamp")
        await Database.db.crime_reports.create_index("crime_type")
        await Database.db.crime_reports.create_index("severity")
        await Database.db.crime_reports.create_index("status")
        
        print("✅ Indexes created successfully")
    except Exception as e:
        print(f"❌ Error creating indexes: {e}")
    finally:
        await Database.close()

if __name__ == "__main__":
    asyncio.run(create_indexes())