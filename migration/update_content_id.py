from sqlalchemy import create_engine, text
from app.config import SQLALCHEMY_DATABASE_URI


def update_content_id_column():
    """Update the content_id column in the watchlist and watch_history tables to use VARCHAR"""
    print("Starting database migration to update content_id columns...")

    # Create engine
    engine = create_engine(SQLALCHEMY_DATABASE_URI)

    try:
        # Connect to the database
        with engine.connect() as connection:
            # Update watchlist table
            print("Updating watchlist table...")
            connection.execute(text("""
                ALTER TABLE watchlist 
                MODIFY COLUMN content_id VARCHAR(50)
            """))
            print("Successfully updated watchlist.content_id column to VARCHAR(50)")

            # Update watch_history table
            print("Updating watch_history table...")
            connection.execute(text("""
                ALTER TABLE watch_history 
                MODIFY COLUMN content_id VARCHAR(50)
            """))
            print("Successfully updated watch_history.content_id column to VARCHAR(50)")

            # Commit the transaction
            connection.commit()
            print("Migration completed successfully")

    except Exception as e:
        print(f"Error updating content_id columns: {str(e)}")
        raise


if __name__ == "__main__":
    update_content_id_column()
