"""
Create admin user for Feishu HR Translator Web UI.

Usage:
    python scripts/create_admin.py
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import SessionLocal, init_db
from backend.models.user import User
from backend.auth.password import get_password_hash


def create_admin_user():
    """Create admin user account."""
    # Initialize database tables
    print("[DATABASE] Initializing database...")
    init_db()

    # Create database session
    db = SessionLocal()

    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("[WARNING] Admin user already exists!")
            print(f"   Username: {existing_admin.username}")
            print(f"   Email: {existing_admin.email}")
            print(f"   Role: {existing_admin.role}")
            return

        # Create admin user
        print("[CREATE] Creating admin user...")
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            email="admin@example.com",
            full_name="System Administrator",
            role="admin",
            is_active=True,
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print("[SUCCESS] Admin user created successfully!")
        print("")
        print("=== Login Credentials ===")
        print("   Username: admin")
        print("   Password: admin123")
        print("")
        print("[SECURITY] Please change the password after first login!")
        print("")
        print("[ACCESS] Web interface at: http://localhost:8080")

    except Exception as e:
        print(f"[ERROR] Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_admin_user()
