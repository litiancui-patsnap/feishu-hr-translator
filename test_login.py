"""
Test login functionality
"""
import asyncio
from backend.database import SessionLocal
from backend.models.user import User
from backend.auth.password import verify_password, get_password_hash

def test_login():
    db = SessionLocal()
    try:
        # Find admin user
        user = db.query(User).filter(User.username == "admin").first()

        if not user:
            print("❌ User 'admin' not found in database")
            return

        print(f"✅ Found user: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Role: {user.role}")
        print(f"   Active: {user.is_active}")
        print(f"   Stored hash: {user.hashed_password}")

        # Test password verification
        test_password = "admin123"
        expected_hash = get_password_hash(test_password)

        print(f"\n🔐 Password Test:")
        print(f"   Test password: {test_password}")
        print(f"   Expected hash: {expected_hash}")
        print(f"   Stored hash:   {user.hashed_password}")
        print(f"   Hash match: {expected_hash == user.hashed_password}")

        # Verify password
        is_valid = verify_password(test_password, user.hashed_password)
        print(f"   Password valid: {is_valid}")

        if is_valid:
            print("\n✅ Login credentials are CORRECT!")
            print("   Username: admin")
            print("   Password: admin123")
        else:
            print("\n❌ Password verification FAILED!")

    finally:
        db.close()

if __name__ == "__main__":
    test_login()
