"""
TaskFlow Database Seeder
CLI script to seed demo user, default categories, and sample tasks into MySQL database.
Usage:
    python backend/seed_data.py
"""
import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from datetime import datetime
from backend.app.database import SessionLocal, Base, engine
from backend.app.models.user import User
from backend.app.auth.security import get_password_hash
from backend.app.services.seed_service import seed_user_data


if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def run_seed():
    print("[INFO] Connecting to database and seeding demo data...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        demo_email = "demo@taskflow.dev"
        user = db.query(User).filter(User.email == demo_email).first()
        if not user:
            print(f"[INFO] Creating demo user: {demo_email}")
            user = User(
                name="Alex Morgan",
                email=demo_email,
                password_hash=get_password_hash("Password123!"),
                is_active=1,
                last_login=datetime.utcnow()
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            print(f"[INFO] Demo user already exists: {demo_email}")

        result = seed_user_data(db, user)
        print("[SUCCESS] Seeding complete!")
        print(f"   Categories created: {result['categories_created']}")
        print(f"   Tasks created: {result['tasks_created']}")
        print(f"   Message: {result['message']}")
        print("\n[CREDENTIALS] Demo Login Details:")
        print("   Email:    demo@taskflow.dev")
        print("   Password: Password123!")
    except Exception as e:
        print(f"[ERROR] Error during seed: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
