from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from typing import List, Dict
from pymongo import DESCENDING
from database import Database
from auth import get_current_user

router = APIRouter()

async def get_date_filter(time_range: str) -> Dict:
    now = datetime.utcnow()
    if time_range == "day":
        start_date = now - timedelta(days=1)
    elif time_range == "week":
        start_date = now - timedelta(weeks=1)
    elif time_range == "month":
        start_date = now - timedelta(days=30)
    else:
        start_date = now - timedelta(days=365)
    
    return {"timestamp": {"$gte": start_date}}

@router.get("/api/crimes/heatmap")
async def get_heatmap_data(
    time_range: str = "week",
    current_user: dict = Depends(get_current_user)
):
    try:
        date_filter = await get_date_filter(time_range)
        
        pipeline = [
            {"$match": date_filter},
            {"$project": {
                "location": 1,
                "crime_type": 1,
                "severity": 1,
                "timestamp": 1
            }}
        ]
        
        cursor = Database.db.crime_reports.aggregate(pipeline)
        crimes = await cursor.to_list(length=None)
        
        return crimes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/crimes/analytics")
async def get_analytics_data(
    time_range: str = "month",
    current_user: dict = Depends(get_current_user)
):
    try:
        date_filter = await get_date_filter(time_range)
        
        # Basic statistics
        basic_stats = await Database.db.crime_reports.aggregate([
            {"$match": date_filter},
            {"$group": {
                "_id": None,
                "total_crimes": {"$sum": 1},
                "avg_crimes_per_day": {"$avg": {"$size": "$crimes"}},
            }}
        ]).to_list(length=1)

        # Crime type distribution
        crime_types = await Database.db.crime_reports.aggregate([
            {"$match": date_filter},
            {"$group": {
                "_id": "$crime_type",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]).to_list(length=None)

        # Severity distribution
        severity_dist = await Database.db.crime_reports.aggregate([
            {"$match": date_filter},
            {"$group": {
                "_id": "$severity",
                "count": {"$sum": 1}
            }}
        ]).to_list(length=None)

        # Status distribution
        status_dist = await Database.db.crime_reports.aggregate([
            {"$match": date_filter},
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }}
        ]).to_list(length=None)

        # Time-based analysis
        time_analysis = await Database.db.crime_reports.aggregate([
            {"$match": date_filter},
            {"$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$timestamp"
                    }
                },
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]).to_list(length=None)

        # Hot zones (areas with high crime rates)
        hot_zones = await Database.db.crime_reports.aggregate([
            {"$match": date_filter},
            {"$group": {
                "_id": {
                    "location": {
                        "$round": [
                            "$location.coordinates",
                            3  # Round to 3 decimal places for area grouping
                        ]
                    }
                },
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]).to_list(length=None)

        return {
            "basic_stats": basic_stats[0] if basic_stats else {},
            "crime_types": crime_types,
            "severity_distribution": severity_dist,
            "status_distribution": status_dist,
            "time_analysis": time_analysis,
            "hot_zones": hot_zones
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/crimes/trends")
async def get_crime_trends(
    time_range: str = "month",
    current_user: dict = Depends(get_current_user)
):
    try:
        date_filter = await get_date_filter(time_range)
        
        # Crime type trends over time
        trends = await Database.db.crime_reports.aggregate([
            {"$match": date_filter},
            {"$group": {
                "_id": {
                    "date": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$timestamp"
                        }
                    },
                    "crime_type": "$crime_type"
                },
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id.date": 1}}
        ]).to_list(length=None)

        return trends
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))