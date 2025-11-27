import sqlite3
import csv
import logging
from pathlib import Path
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for managing in-memory SQLite database"""

    def __init__(self):
        self.conn = None
        self.cursor = None

    def initialize(self):
        """Initialize in-memory database and load CSV data"""
        logger.info("=" * 80)
        logger.info("🗄️  DATABASE INITIALIZATION")
        logger.info("=" * 80)

        # Create in-memory SQLite database
        logger.info("📦 Creating in-memory SQLite database...")
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.cursor = self.conn.cursor()
        logger.info("✅ Database connection established")

        # Load CSV data
        csv_path = Path(__file__).parent / "cybersecurity_attacks.csv"
        if not csv_path.exists():
            logger.error(f"❌ CSV file not found: {csv_path}")
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        logger.info(f"📂 Loading data from: {csv_path}")
        self._load_csv(csv_path)

    def _load_csv(self, csv_path: Path):
        """Load CSV data into SQLite database"""
        with open(csv_path, 'r', encoding='utf-8') as f:
            csv_reader = csv.reader(f)
            headers = next(csv_reader)

            logger.info(f"📋 Found {len(headers)} columns")

            # Create table with all columns as TEXT for simplicity
            column_definitions = ", ".join([f'"{col}" TEXT' for col in headers])
            create_table_sql = f"CREATE TABLE attacks ({column_definitions})"
            self.cursor.execute(create_table_sql)
            logger.info("✅ Created 'attacks' table")

            # Insert data
            placeholders = ", ".join(["?" for _ in headers])
            insert_sql = f"INSERT INTO attacks VALUES ({placeholders})"

            batch = []
            total_rows = 0
            for row in csv_reader:
                batch.append(row)
                if len(batch) >= 1000:
                    self.cursor.executemany(insert_sql, batch)
                    total_rows += len(batch)
                    logger.info(f"   Inserted {total_rows} rows...")
                    batch = []

            # Insert remaining rows
            if batch:
                self.cursor.executemany(insert_sql, batch)
                total_rows += len(batch)

            self.conn.commit()

            logger.info(f"✅ Successfully loaded {total_rows} rows into database")
            logger.info("=" * 80)
            logger.info("")

    def query(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Execute SQL query and return results as list of dictionaries

        Args:
            sql: SQL query string
            params: Query parameters for parameterized queries

        Returns:
            List of dictionaries with column names as keys
        """
        if not self.conn:
            raise RuntimeError("Database not initialized")

        self.cursor.execute(sql, params)
        columns = [description[0] for description in self.cursor.description]
        results = []

        for row in self.cursor.fetchall():
            results.append(dict(zip(columns, row)))

        return results

    def get_table_info(self) -> Dict[str, Any]:
        """Get information about the attacks table"""
        if not self.conn:
            raise RuntimeError("Database not initialized")

        # Get column names and types
        self.cursor.execute("PRAGMA table_info(attacks)")
        columns = self.cursor.fetchall()

        # Get row count
        self.cursor.execute("SELECT COUNT(*) FROM attacks")
        row_count = self.cursor.fetchone()[0]

        return {
            "table_name": "attacks",
            "columns": [{"name": col[1], "type": col[2]} for col in columns],
            "row_count": row_count
        }

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


# Global database instance
db = DatabaseService()
