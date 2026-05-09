"""
Initialize database with sample data
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
import random

from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models import User, Device, EnergyRecord, Product, PointsHistory, Redemption
from app.core.security import get_password_hash


def init_db():
    # Create all tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Check if data already exists
        if db.query(User).first():
            print("Database already initialized. Skipping...")
            return

        print("Initializing database with sample data...")

        # Create admin user
        admin = User(
            email="admin@example.com",
            username="admin",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin User",
            department="IT",
            is_active=True,
            is_superuser=True,
            points_balance=5000
        )
        db.add(admin)

        # Create regular users
        users = []
        departments = ["営業部", "開発部", "総務部", "経理部", "人事部"]
        for i in range(1, 11):
            user = User(
                email=f"user{i}@example.com",
                username=f"user{i}",
                hashed_password=get_password_hash("password123"),
                full_name=f"ユーザー {i}",
                department=random.choice(departments),
                is_active=True,
                is_superuser=False,
                points_balance=random.randint(100, 3000)
            )
            users.append(user)
            db.add(user)

        db.commit()

        # Create devices for admin
        device_types = ["solar_panel", "battery", "smart_meter", "ev_charger"]
        devices = []
        for i in range(1, 6):
            device = Device(
                name=f"デバイス {i}",
                device_type=random.choice(device_types),
                model=f"Model-{random.randint(100, 999)}",
                serial_number=f"SN-{random.randint(10000, 99999)}",
                capacity=random.uniform(5.0, 20.0),
                efficiency=random.uniform(0.85, 0.98),
                location=f"Building {chr(65 + i % 5)}",
                is_active=True,
                installation_date=datetime.now() - timedelta(days=random.randint(30, 365)),
                owner_id=admin.id
            )
            devices.append(device)
            db.add(device)

        db.commit()

        # Create energy records for the past 30 days
        for device in devices:
            for day in range(30):
                record_date = datetime.now() - timedelta(days=day)
                record = EnergyRecord(
                    timestamp=record_date,
                    energy_produced=random.uniform(10, 50),
                    energy_consumed=random.uniform(20, 80),
                    energy_stored=random.uniform(5, 30),
                    grid_import=random.uniform(0, 20),
                    grid_export=random.uniform(0, 15),
                    voltage=random.uniform(220, 240),
                    current=random.uniform(5, 20),
                    power=random.uniform(1000, 5000),
                    temperature=random.uniform(20, 35),
                    efficiency=random.uniform(0.8, 0.95),
                    status="normal",
                    gas_usage=random.uniform(1, 10),
                    co2_reduction=random.uniform(5, 25),
                    device_id=device.id,
                    user_id=admin.id
                )
                db.add(record)

        db.commit()

        # Create products/rewards
        products_data = [
            {"title": "Amazonギフトカード 1000円", "description": "Amazonで使えるギフトカード", "category": "ギフトカード", "points_required": 1000, "stock": 100},
            {"title": "Amazonギフトカード 5000円", "description": "Amazonで使えるギフトカード", "category": "ギフトカード", "points_required": 5000, "stock": 50},
            {"title": "スターバックスカード 500円", "description": "スターバックスで使えるプリペイドカード", "category": "ギフトカード", "points_required": 500, "stock": 200},
            {"title": "エコバッグ", "description": "環境に優しいエコバッグ", "category": "グッズ", "points_required": 300, "stock": 500},
            {"title": "マイボトル", "description": "保温保冷マイボトル 500ml", "category": "グッズ", "points_required": 800, "stock": 100},
            {"title": "ソーラーモバイルバッテリー", "description": "太陽光で充電できるモバイルバッテリー", "category": "電子機器", "points_required": 2000, "stock": 30},
            {"title": "LED電球セット", "description": "省エネLED電球 4個セット", "category": "省エネグッズ", "points_required": 600, "stock": 150},
            {"title": "節水シャワーヘッド", "description": "水道代を節約できるシャワーヘッド", "category": "省エネグッズ", "points_required": 1500, "stock": 50},
        ]

        products = []
        for p_data in products_data:
            product = Product(**p_data, active=True)
            products.append(product)
            db.add(product)

        db.commit()

        # Create some points history and redemptions
        for user in users[:5]:
            # Earn points history
            for _ in range(random.randint(3, 10)):
                history = PointsHistory(
                    user_id=user.id,
                    type="earn",
                    points=random.randint(50, 500),
                    description="省エネ達成ボーナス",
                    created_at=datetime.now() - timedelta(days=random.randint(1, 30))
                )
                db.add(history)

            # Some redemptions
            if random.random() > 0.5:
                product = random.choice(products)
                redemption = Redemption(
                    user_id=user.id,
                    product_id=product.id,
                    points_spent=product.points_required,
                    status="completed"
                )
                db.add(redemption)

                redeem_history = PointsHistory(
                    user_id=user.id,
                    type="redeem",
                    points=-product.points_required,
                    description=f"交換: {product.title}"
                )
                db.add(redeem_history)

        db.commit()

        print("Database initialized successfully!")
        print("\nTest accounts:")
        print("  Admin: admin@example.com / admin123")
        print("  User:  user1@example.com / password123")

    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
