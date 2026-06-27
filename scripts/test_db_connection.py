#!/usr/bin/env python3
"""
Database Connectivity Test Script
---------------------------------
Tests whether Django can connect to the configured database.
Supports both PostgreSQL (local) and Azure SQL Database (production).

Usage:
    python scripts/test_db_connection.py

Environment variables required:
    DB_ENGINE, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
"""
import os
import sys
import django

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

try:
    django.setup()
except Exception as e:
    print(f"[FAIL] Django setup failed: {e}")
    sys.exit(1)

from django.db import connection


def test_connection():
    print("=" * 60)
    print("Purdue Capstone — Database Connectivity Test")
    print("=" * 60)

    # Show config (mask password)
    db_config = connection.settings_dict
    print(f"Engine:   {db_config.get('ENGINE')}")
    print(f"Name:     {db_config.get('NAME')}")
    print(f"Host:     {db_config.get('HOST')}")
    print(f"Port:     {db_config.get('PORT')}")
    print(f"User:     {db_config.get('USER')}")
    print(f"Password: {'*' * len(str(db_config.get('PASSWORD', '')))}")
    print("-" * 60)

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            row = cursor.fetchone()
            if row and row[0] == 1:
                print("[PASS] Database connection successful.")

                # Try to list tables
                engine = db_config.get("ENGINE", "")
                if "postgresql" in engine:
                    cursor.execute(
                        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
                    )
                elif "mssql" in engine or "sqlserver" in engine:
                    cursor.execute("SELECT name FROM sys.tables")
                else:
                    cursor.execute("SHOW TABLES")

                tables = [r[0] for r in cursor.fetchall()]
                print(f"[INFO] Tables found: {len(tables)}")
                for t in tables[:10]:
                    print(f"       - {t}")
                if len(tables) > 10:
                    print(f"       ... and {len(tables) - 10} more")

                print("-" * 60)
                print("RESULT: All checks passed. Database is ready.")
                return 0
            else:
                print("[FAIL] Connection returned unexpected result.")
                return 1
    except Exception as e:
        print(f"[FAIL] Database connection failed: {e}")
        print("-" * 60)
        print("TROUBLESHOOTING:")
        print("  1. Verify the database server is running.")
        print("  2. Check firewall rules allow your IP (Azure SQL).")
        print("  3. Verify username/password are correct.")
        print("  4. Ensure the database name exists on the server.")
        print("  5. For Azure SQL, confirm ODBC Driver 18 is installed.")
        return 1


if __name__ == "__main__":
    sys.exit(test_connection())
