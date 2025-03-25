import asyncio
from auth import get_password_hash
from database import db, init_db, close_db

async def create_test_user():
    try:
        # Initialize database
        await init_db()
        
        # Test user data
        test_user = {
            "username": "admin",
            "email": "admin@example.com",
            "hashed_password": get_password_hash("admin123"),
            "full_name": "Admin User",
            "disabled": False
        }
        
        # Delete existing user if any
        await db.users.delete_one({"username": "admin"})
        
        # Create new test user
        result = await db.users.insert_one(test_user)
        
        print("\n✅ Test user created successfully!")
        print("\nLogin credentials:")
        print("------------------")
        print("Username: admin")
        print("Password: admin123")
        print("------------------")
        
    except Exception as e:
        print(f"\n❌ Error creating test user: {e}")
    finally:
        await close_db()

if __name__ == "__main__":
    asyncio.run(create_test_user())
