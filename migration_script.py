from sqlalchemy import create_engine, text
from app.core.config import DATABASE_URL

def run_migration():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        try:
            # Check if column exists first to avoid error
            # SQLite doesn't support IF NOT EXISTS for ADD COLUMN in older versions, but let's try simple ADD COLUMN
            # If it fails, it might already exist.
            connection.execute(text("ALTER TABLE inventory_items ADD COLUMN manufacturer_part_number VARCHAR"))
            print("Migration successful: Added manufacturer_part_number column.")
        except Exception as e:
            print(f"Migration failed (might already exist): {e}")

if __name__ == "__main__":
    run_migration()
