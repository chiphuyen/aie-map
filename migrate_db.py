import sqlite3
import os

def migrate_database():
    """Migrate existing database to new schema"""
    db_path = "aie_map.db"
    
    if not os.path.exists(db_path):
        print("No existing database found. New database will be created automatically.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if new columns exist
        cursor.execute("PRAGMA table_info(reviews)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Add social_media_url column if it doesn't exist
        if 'social_media_url' not in columns:
            print("Adding social_media_url column...")
            cursor.execute("ALTER TABLE reviews ADD COLUMN social_media_url TEXT")
        
        # Check if review_assets table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='review_assets'")
        if not cursor.fetchone():
            print("Creating review_assets table...")
            cursor.execute("""
                CREATE TABLE review_assets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    review_id INTEGER NOT NULL,
                    file_path VARCHAR(500) NOT NULL,
                    file_name VARCHAR(255),
                    file_type VARCHAR(50),
                    file_size INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (review_id) REFERENCES reviews(id) ON DELETE CASCADE
                )
            """)
        
        conn.commit()
        print("Database migration completed successfully!")
        
    except Exception as e:
        print(f"Migration error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()