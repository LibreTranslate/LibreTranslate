import sqlite3
from pathlib import Path

# Database file path (e.g., db/tm.db)
# Assuming the script is run from the project root or that 'db' directory is accessible.
DB_DIR = Path(__file__).resolve().parent.parent / "db"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_FILE = DB_DIR / "tm.db"

class TMDatabase:
    def __init__(self, db_path=DB_FILE):
        """
        Initializes the TMDatabase.

        Args:
            db_path (str, optional): Path to the SQLite database file.
                                     Defaults to DB_FILE.
        """
        self.db_path = db_path
        self._create_table_if_not_exists()

    def _get_connection(self):
        """Establishes and returns a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Access columns by name
        return conn

    def _create_table_if_not_exists(self):
        """
        Creates the 'translation_memory' table and its index if they don't exist.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS translation_memory (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source_text TEXT NOT NULL,
                        target_text TEXT NOT NULL,
                        source_lang VARCHAR(10) NOT NULL,
                        target_lang VARCHAR(10) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        user_id INTEGER NULLABLE,
                        confidence REAL NULLABLE
                    )
                """)
                # Create an index for faster lookups
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_tm_lookup
                    ON translation_memory (source_text, source_lang, target_lang)
                """)
                conn.commit()
        except sqlite3.Error as e:
            print(f"Database error during table creation: {e}")
            # Depending on the application's needs, you might want to raise the exception
            # or handle it more gracefully (e.g., log and exit).
            raise

    def add_entry(self, source_text, target_text, source_lang, target_lang, user_id=None, confidence=None):
        """
        Adds a new translation entry to the database.

        Args:
            source_text (str): The source text.
            target_text (str): The translated target text.
            source_lang (str): The source language code.
            target_lang (str): The target language code.
            user_id (int, optional): The ID of the user adding the entry. Defaults to None.
            confidence (float, optional): The confidence score of the translation. Defaults to None.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO translation_memory 
                                (source_text, target_text, source_lang, target_lang, user_id, confidence, last_used_at)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (source_text, target_text, source_lang, target_lang, user_id, confidence))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Database error when adding entry: {e}")
            # Consider logging the error or re-raising if critical

    def lookup_entry(self, source_text, source_lang, target_lang):
        """
        Looks up a translation entry in the database.

        Args:
            source_text (str): The source text to look up.
            source_lang (str): The source language code.
            target_lang (str): The target language code.

        Returns:
            tuple: (target_text, entry_id) if found, else None.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, target_text FROM translation_memory
                    WHERE source_text = ? AND source_lang = ? AND target_lang = ?
                    ORDER BY last_used_at DESC, confidence DESC
                    LIMIT 1 
                """, (source_text, source_lang, target_lang))
                row = cursor.fetchone()
                if row:
                    return row['target_text'], row['id']
            return None
        except sqlite3.Error as e:
            print(f"Database error during lookup: {e}")
            return None

    def update_last_used(self, entry_id):
        """
        Updates the 'last_used_at' timestamp for a given entry ID.

        Args:
            entry_id (int): The ID of the translation memory entry to update.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE translation_memory
                    SET last_used_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (entry_id,))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Database error when updating last_used_at: {e}")
            # Consider logging the error

    def list_entries(self, page=1, per_page=20, source_lang=None, target_lang=None):
        """
        Retrieves a paginated list of TM entries, optionally filtered by language.

        Args:
            page (int): The page number to retrieve.
            per_page (int): The number of entries per page.
            source_lang (str, optional): Filter by source language code (model code).
            target_lang (str, optional): Filter by target language code (model code).

        Returns:
            tuple: (list of dicts representing entries, total_count of matching entries)
        """
        offset = (page - 1) * per_page
        base_query = "SELECT id, source_text, target_text, source_lang, target_lang, created_at, last_used_at, user_id, confidence FROM translation_memory"
        count_query = "SELECT COUNT(*) as count FROM translation_memory"
        
        conditions = []
        params = []

        if source_lang:
            conditions.append("source_lang = ?")
            params.append(source_lang)
        if target_lang:
            conditions.append("target_lang = ?")
            params.append(target_lang)

        if conditions:
            where_clause = " WHERE " + " AND ".join(conditions)
            base_query += where_clause
            count_query += where_clause
        
        base_query += " ORDER BY id DESC LIMIT ? OFFSET ?"
        params_paginated = params + [per_page, offset]

        entries = []
        total_count = 0

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Get total count
                cursor.execute(count_query, params)
                row = cursor.fetchone()
                if row:
                    total_count = row['count']
                
                # Get paginated entries
                cursor.execute(base_query, params_paginated)
                entries = [dict(row) for row in cursor.fetchall()] # Convert rows to dicts
            return entries, total_count
        except sqlite3.Error as e:
            print(f"Database error listing entries: {e}")
            return [], 0

    def delete_entry(self, entry_id):
        """
        Deletes a TM entry by its ID.

        Args:
            entry_id (int): The ID of the entry to delete.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM translation_memory WHERE id = ?", (entry_id,))
                conn.commit()
                return cursor.rowcount > 0  # rowcount is the number of rows affected
        except sqlite3.Error as e:
            print(f"Database error deleting entry {entry_id}: {e}")
            return False

    def get_entry_by_id(self, entry_id):
        """
        Retrieves a single TM entry by its ID.

        Args:
            entry_id (int): The ID of the entry to retrieve.

        Returns:
            dict: A dictionary representing the entry if found, else None.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, source_text, target_text, source_lang, target_lang, 
                           created_at, last_used_at, user_id, confidence 
                    FROM translation_memory WHERE id = ?
                """, (entry_id,))
                row = cursor.fetchone()
                if row:
                    return dict(row)
            return None
        except sqlite3.Error as e:
            print(f"Database error getting entry {entry_id}: {e}")
            return None

if __name__ == '__main__':
    # Example usage (for testing purposes)
    # This will create the db/tm.db file if it doesn't exist
    tm_db_instance = TMDatabase()
    print(f"TMDatabase initialized. Database file at: {tm_db_instance.db_path}")
    # You could add a dummy entry here to test
    # tm_db_instance.add_entry("Hello", "Hola", "en", "es")
    # result = tm_db_instance.lookup_entry("Hello", "en", "es")
    # if result:
    #     print(f"Lookup result: {result}")

    # Verify table and index creation by inspecting the database file
    # using a tool like DB Browser for SQLite.
    print("Please verify the 'translation_memory' table and 'idx_tm_lookup' index in the database.")
