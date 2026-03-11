"""
Migration: Add linkedin_email and linkedin_password_encrypted columns to users table.

Run once:
    python scripts/add_linkedin_columns.py

Safe to re-run — uses IF NOT EXISTS / catches duplicate-column errors.
"""
import asyncio
import sys
import os

# Allow running from repo root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def main():
    from app.backend.database.connection import engine

    async with engine.begin() as conn:
        for col_sql in [
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS linkedin_email VARCHAR(255)",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS linkedin_password_encrypted TEXT",
        ]:
            try:
                await conn.execute(__import__("sqlalchemy").text(col_sql))
                print(f"✅ {col_sql}")
            except Exception as e:
                # Ignore "column already exists" errors from databases that
                # don't support IF NOT EXISTS (e.g. older SQLite versions)
                msg = str(e).lower()
                if "already exists" in msg or "duplicate column" in msg:
                    print(f"⏭  Column already exists — skipping.")
                else:
                    print(f"❌ Error: {e}")
                    raise

    print("\nMigration complete.")


if __name__ == "__main__":
    asyncio.run(main())
