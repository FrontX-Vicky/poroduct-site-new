"""Fill the database with demo categories, products and a demo user.

Run from backend/:  python -m app.seed
Safe to run more than once: it does nothing if categories already exist.
"""
from sqlalchemy import select

from . import models
from .auth import hash_password
from .config import DEMO_EMAIL, DEMO_PASSWORD
from .database import Base, SessionLocal, engine

CATALOG = {
    "Electronics": [
        ("Apple iPhone 15 (128 GB) - Black", "6.1-inch Super Retina XDR display, A16 Bionic chip, 48MP camera.", 69900, 25),
        ("Samsung Galaxy S24 Ultra (256 GB)", "Titanium frame, S Pen built in, 200MP camera, Galaxy AI.", 121999, 12),
        ("Sony WH-1000XM5 Wireless Headphones", "Industry-leading noise cancellation, 30-hour battery life.", 29990, 40),
        ("boAt Airdopes 141 Earbuds", "42H playtime, ENx noise cancellation, low-latency gaming mode.", 1099, 150),
        ("Apple MacBook Air M3 13-inch", "8GB RAM, 256GB SSD, Liquid Retina display, 18-hour battery.", 114900, 8),
    ],
    "Books": [
        ("Atomic Habits by James Clear", "An easy and proven way to build good habits and break bad ones.", 499, 200),
        ("The Psychology of Money by Morgan Housel", "Timeless lessons on wealth, greed and happiness.", 349, 180),
        ("Ikigai: The Japanese Secret to a Long and Happy Life", "Finding purpose and joy in everyday life.", 299, 120),
        ("Rich Dad Poor Dad by Robert Kiyosaki", "What the rich teach their kids about money.", 399, 90),
        ("The Alchemist by Paulo Coelho", "A fable about following your dream.", 279, 0),
    ],
    "Home & Kitchen": [
        ("Prestige Iris 750W Mixer Grinder", "3 stainless steel jars, 5-year motor warranty.", 3199, 35),
        ("Pigeon Non-Stick Cookware Set (3 pcs)", "Fry pan, kadai and tawa with induction base.", 1299, 60),
        ("Milton Thermosteel Flask 1 Litre", "Keeps drinks hot or cold for 24 hours.", 899, 100),
        ("Philips Air Fryer HD9252", "Rapid Air technology, 4.1 L capacity, 90% less fat.", 7999, 18),
        ("Solimo Microfibre Bedsheet Set (Double)", "1 bedsheet with 2 pillow covers, soft and wrinkle-free.", 549, 75),
    ],
    "Fashion": [
        ("Levi's Men's 511 Slim Fit Jeans", "Stretch denim, mid-rise, dark indigo wash.", 2399, 50),
        ("Puma Men's Running Shoes", "Lightweight mesh upper with cushioned SoftFoam+ sole.", 3299, 40),
        ("Allen Solly Women's Regular Fit Top", "Cotton blend, casual everyday wear.", 899, 65),
        ("Fastrack Analog Watch for Men", "Stainless steel case, water resistant, black dial.", 1695, 30),
        ("Wildcraft 45L Rucksack", "Durable backpack with rain cover for travel and trekking.", 2199, 22),
    ],
    "Sports & Fitness": [
        ("Boldfit Yoga Mat 6mm", "Anti-slip, extra thick, with carrying strap.", 499, 140),
        ("Cosco Football Size 5", "Machine-stitched, suitable for all surfaces.", 799, 55),
        ("Kore PVC 20kg Home Gym Set", "Dumbbell rods, plates and accessories for home workouts.", 1499, 20),
        ("Yonex Mavis 350 Shuttlecocks (Pack of 6)", "Nylon shuttles with consistent flight.", 1150, 80),
        ("SG Kashmir Willow Cricket Bat", "Full size, ideal for leather ball practice.", 1899, 15),
    ],
}


def seed():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.scalar(select(models.Category)):
            print("Database already has data - skipping seed.")
            return

        user = db.scalar(select(models.User).where(models.User.email == DEMO_EMAIL))
        if user is None:
            user = models.User(email=DEMO_EMAIL, password_hash=hash_password(DEMO_PASSWORD))
            db.add(user)
            db.flush()

        for category_name, products in CATALOG.items():
            category = models.Category(name=category_name)
            db.add(category)
            db.flush()
            for name, description, price, stock in products:
                db.add(models.Product(name=name, description=description, price=price, stock=stock,
                                      category_id=category.id, created_by=user.id))
        db.commit()
        print(f"Seeded {len(CATALOG)} categories and {sum(map(len, CATALOG.values()))} products.")
        print(f"Demo login: {DEMO_EMAIL} / {DEMO_PASSWORD}")


if __name__ == "__main__":
    seed()
