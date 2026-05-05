import sys
import os

# Add the project root to python path
sys.path.append(os.path.join(os.getcwd(), "app"))
sys.path.append(os.getcwd())

from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import hash_password

def create_admin():
    db = SessionLocal()
    try:
        # Check if admin exists
        admin_email = "admin@nexusai.com"
        admin = db.query(User).filter(User.email == admin_email).first()
        
        if admin:
            print(f"Admin user already exists: {admin_email}")
            # Ensure it's an admin
            admin.role = "admin"
            db.commit()
            print("Role verified as admin.")
        else:
            new_admin = User(
                full_name="Nexus Admin",
                email=admin_email,
                hashed_password=hash_password("AdminPassword123!"),
                role="admin",
                is_active=True,
                is_verified=True
            )
            db.add(new_admin)
            db.commit()
            print(f"Admin user created successfully!")
            print(f"Email: {admin_email}")
            print(f"Password: AdminPassword123!")
    except Exception as e:
        print(f"Error creating admin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
