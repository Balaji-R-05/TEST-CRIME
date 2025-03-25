from typing import List, Optional
from datetime import datetime, timedelta
from database import Database
from bson import ObjectId

class CrimeReportDB:
    @classmethod
    async def get_collection(cls):
        if Database.db is None:
            await Database.connect()
        return Database.db.crime_reports

    @classmethod
    async def create(cls, report_data: dict) -> str:
        collection = await cls.get_collection()
        result = await collection.insert_one(report_data)
        return str(result.inserted_id)

    @classmethod
    async def get_by_id(cls, report_id: str):
        collection = await cls.get_collection()
        return await collection.find_one({"crime_id": report_id})

    @classmethod
    async def get_by_status(cls, status: str):
        collection = await cls.get_collection()
        return await collection.find({"status": status}).to_list(length=None)

    @classmethod
    async def get_by_officer(cls, badge: str):
        collection = await cls.get_collection()
        return await collection.find({"officer_in_charge.badge": badge}).to_list(length=None)

    @classmethod
    async def get_by_severity(cls, severity: str):
        collection = await cls.get_collection()
        return await collection.find({"severity": severity}).to_list(length=None)

    @classmethod
    async def get_by_tags(cls, tags: List[str]):
        collection = await cls.get_collection()
        return await collection.find({"tags": {"$in": tags}}).to_list(length=None)

    @classmethod
    async def update_status(cls, crime_id: str, new_status: str):
        collection = await cls.get_collection()
        return await collection.update_one(
            {"crime_id": crime_id},
            {"$set": {"status": new_status}}
        )

    @classmethod
    async def get_nearby(cls, longitude: float, latitude: float, max_distance: int = 5000):
        collection = await cls.get_collection()
        pipeline = [
            {
                "$geoNear": {
                    "near": {"type": "Point", "coordinates": [longitude, latitude]},
                    "distanceField": "distance",
                    "maxDistance": max_distance,
                    "spherical": True
                }
            },
            {
                "$sort": {"date_time": -1}
            }
        ]
        return await collection.aggregate(pipeline).to_list(length=50)

    @classmethod
    async def get_by_user(cls, user_id: str, skip: int = 0, limit: int = 20):
        cursor = cls.collection.find({"user_id": user_id})
        cursor.sort("created_at", -1).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)

    @classmethod
    async def get_crime_heatmap_data(cls, start_date=None, end_date=None, crime_type=None):
        collection = await cls.get_collection()
        query = {}
        
        if start_date and end_date:
            query["date_time"] = {
                "$gte": start_date,
                "$lte": end_date
            }
        
        if crime_type:
            query["crime_type"] = crime_type
        
        pipeline = [
            {"$match": query},
            {
                "$project": {
                    "location": 1,
                    "crime_type": 1,
                    "weight": {
                        "$switch": {
                            "branches": [
                                {"case": {"$eq": ["$crime_type", "assault"]}, "then": 3},
                                {"case": {"$eq": ["$crime_type", "robbery"]}, "then": 3},
                                {"case": {"$eq": ["$crime_type", "burglary"]}, "then": 2},
                            ],
                            "default": 1
                        }
                    }
                }
            }
        ]
        
        return await collection.aggregate(pipeline).to_list(None)

    @classmethod
    async def get_crime_statistics(cls, days=30):
        collection = await cls.get_collection()
        start_date = datetime.utcnow() - timedelta(days=days)
        
        pipeline = [
            {
                "$match": {
                    "date_time": {"$gte": start_date}
                }
            },
            {
                "$group": {
                    "_id": {
                        "crime_type": "$crime_type",
                        "status": "$status"
                    },
                    "count": {"$sum": 1}
                }
            },
            {
                "$group": {
                    "_id": "$_id.crime_type",
                    "stats": {
                        "$push": {
                            "status": "$_id.status",
                            "count": "$count"
                        }
                    },
                    "total": {"$sum": "$count"}
                }
            }
        ]
        
        return await collection.aggregate(pipeline).to_list(None)


