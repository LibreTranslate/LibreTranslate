import unittest
import sqlite3
import time
from pathlib import Path
from libretranslate.tm_db import TMDatabase

# Use a specific directory for test databases if needed, or just use in-memory
TEST_DB_DIR = Path(__file__).resolve().parent / "test_dbs"
TEST_DB_DIR.mkdir(parents=True, exist_ok=True)

class TestTMDatabase(unittest.TestCase):

    def setUp(self):
        """Set up a new in-memory database for each test."""
        # self.db_path = TEST_DB_DIR / f"test_tm_{time.time_ns()}.db" # For file-based test DB
        self.db_path = ":memory:" # For in-memory DB
        self.tm_db = TMDatabase(db_path=self.db_path)
        # print(f"Using DB: {self.db_path}") # For debugging if file-based

    def tearDown(self):
        """Clean up the database connection. If file-based, remove the DB file."""
        conn = self.tm_db._get_connection()
        if conn:
            conn.close()
        # if self.db_path != ":memory:" and Path(self.db_path).exists():
        #     Path(self.db_path).unlink()
        #     # print(f"Cleaned up DB: {self.db_path}") # For debugging

    def test_01_create_table(self):
        """Test if the table and index are created."""
        with self.tm_db._get_connection() as conn:
            cursor = conn.cursor()
            # Check for table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='translation_memory';")
            self.assertIsNotNone(cursor.fetchone(), "Table 'translation_memory' should exist.")
            # Check for index
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_tm_lookup';")
            self.assertIsNotNone(cursor.fetchone(), "Index 'idx_tm_lookup' should exist.")

    def test_02_add_entry(self):
        """Test adding a new translation entry."""
        self.tm_db.add_entry("Hello", "Hola", "en", "es", user_id=1, confidence=0.9)
        with self.tm_db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM translation_memory WHERE source_text='Hello'")
            entry = cursor.fetchone()
            self.assertIsNotNone(entry)
            self.assertEqual(entry["target_text"], "Hola")
            self.assertEqual(entry["source_lang"], "en")
            self.assertEqual(entry["target_lang"], "es")
            self.assertEqual(entry["user_id"], 1)
            self.assertEqual(entry["confidence"], 0.9)

    def test_03_lookup_entry_found(self):
        """Test looking up an existing entry."""
        self.tm_db.add_entry("Hello", "Hola", "en", "es")
        # Add another entry to ensure the correct one is picked
        self.tm_db.add_entry("Hello", "Bonjour", "en", "fr")
        
        result = self.tm_db.lookup_entry("Hello", "en", "es")
        self.assertIsNotNone(result)
        target_text, entry_id = result
        self.assertEqual(target_text, "Hola")
        self.assertIsInstance(entry_id, int)

    def test_04_lookup_entry_not_found(self):
        """Test looking up a non-existent entry."""
        result = self.tm_db.lookup_entry("Goodbye", "en", "es")
        self.assertIsNone(result)

    def test_05_update_last_used(self):
        """Test updating the last_used_at timestamp."""
        self.tm_db.add_entry("Test", "Prueba", "en", "es")
        result = self.tm_db.lookup_entry("Test", "en", "es")
        self.assertIsNotNone(result)
        _, entry_id = result

        with self.tm_db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT last_used_at FROM translation_memory WHERE id=?", (entry_id,))
            timestamp1_str = cursor.fetchone()["last_used_at"]
        
        # Ensure timestamp is a string and convert if necessary for comparison later
        self.assertIsInstance(timestamp1_str, str)
        timestamp1 = time.mktime(time.strptime(timestamp1_str, "%Y-%m-%d %H:%M:%S"))

        # Wait a bit to ensure the timestamp changes
        time.sleep(0.01) # Reduced sleep time for faster tests

        self.tm_db.update_last_used(entry_id)

        with self.tm_db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT last_used_at FROM translation_memory WHERE id=?", (entry_id,))
            timestamp2_str = cursor.fetchone()["last_used_at"]
        
        self.assertIsInstance(timestamp2_str, str)
        timestamp2 = time.mktime(time.strptime(timestamp2_str, "%Y-%m-%d %H:%M:%S"))

        self.assertGreater(timestamp2, timestamp1, "last_used_at should be updated to a later time.")

    def test_06_delete_entry_found(self):
        """Test deleting an existing entry."""
        self.tm_db.add_entry("DeleteMe", "BorrarMe", "en", "es")
        result = self.tm_db.lookup_entry("DeleteMe", "en", "es")
        self.assertIsNotNone(result)
        _, entry_id = result

        deleted = self.tm_db.delete_entry(entry_id)
        self.assertTrue(deleted)

        result_after_delete = self.tm_db.lookup_entry("DeleteMe", "en", "es")
        self.assertIsNone(result_after_delete)

    def test_07_delete_entry_not_found(self):
        """Test deleting a non-existent entry."""
        deleted = self.tm_db.delete_entry(99999) # Assuming this ID won't exist
        self.assertFalse(deleted)

    def test_08_list_entries_basic(self):
        """Test basic listing and pagination."""
        for i in range(25): # Add 25 entries
            self.tm_db.add_entry(f"Text {i}", f"Texto {i}", "en", "es")
        
        entries, total_count = self.tm_db.list_entries(page=1, per_page=10)
        self.assertEqual(len(entries), 10)
        self.assertEqual(total_count, 25)
        self.assertEqual(entries[0]["source_text"], "Text 24") # Ordered by ID DESC

        entries_page2, total_count_p2 = self.tm_db.list_entries(page=2, per_page=10)
        self.assertEqual(len(entries_page2), 10)
        self.assertEqual(total_count_p2, 25)
        self.assertEqual(entries_page2[0]["source_text"], "Text 14")

        entries_page3, total_count_p3 = self.tm_db.list_entries(page=3, per_page=10)
        self.assertEqual(len(entries_page3), 5)
        self.assertEqual(total_count_p3, 25)
        self.assertEqual(entries_page3[0]["source_text"], "Text 4")

    def test_09_list_entries_filtered(self):
        """Test listing entries with language filters."""
        self.tm_db.add_entry("Hello", "Hola", "en", "es")
        self.tm_db.add_entry("Hello", "Bonjour", "en", "fr")
        self.tm_db.add_entry("Goodbye", "Adiós", "en", "es")
        self.tm_db.add_entry("Bonjour", "Hello", "fr", "en")

        # Filter by source_lang
        entries_en_src, count_en_src = self.tm_db.list_entries(source_lang="en")
        self.assertEqual(count_en_src, 3)
        self.assertEqual(len(entries_en_src), 3) # Assuming per_page >= 3

        # Filter by target_lang
        entries_es_tgt, count_es_tgt = self.tm_db.list_entries(target_lang="es")
        self.assertEqual(count_es_tgt, 2)
        self.assertEqual(len(entries_es_tgt), 2)

        # Filter by source_lang and target_lang
        entries_en_fr, count_en_fr = self.tm_db.list_entries(source_lang="en", target_lang="fr")
        self.assertEqual(count_en_fr, 1)
        self.assertEqual(len(entries_en_fr), 1)
        self.assertEqual(entries_en_fr[0]["source_text"], "Hello")
        self.assertEqual(entries_en_fr[0]["target_text"], "Bonjour")
        
        # Filter with no results
        entries_none, count_none = self.tm_db.list_entries(source_lang="de")
        self.assertEqual(count_none, 0)
        self.assertEqual(len(entries_none), 0)

    def test_10_get_entry_by_id_found(self):
        """Test retrieving an entry by its ID."""
        self.tm_db.add_entry("Specific", "Específico", "en", "es")
        # Need to get the ID first
        lookup_res = self.tm_db.lookup_entry("Specific", "en", "es")
        self.assertIsNotNone(lookup_res)
        _, entry_id_to_find = lookup_res

        entry = self.tm_db.get_entry_by_id(entry_id_to_find)
        self.assertIsNotNone(entry)
        self.assertEqual(entry["id"], entry_id_to_find)
        self.assertEqual(entry["source_text"], "Specific")
        self.assertEqual(entry["target_text"], "Específico")

    def test_11_get_entry_by_id_not_found(self):
        """Test retrieving a non-existent entry by ID."""
        entry = self.tm_db.get_entry_by_id(88888) # Assuming this ID won't exist
        self.assertIsNone(entry)

    def test_12_lookup_priority(self):
        """Test that lookup prioritizes by last_used_at and confidence (implicitly, as confidence is not yet updatable)."""
        self.tm_db.add_entry("Repeat", "Repetir_v1", "en", "es", confidence=0.8)
        _, entry_id_v1 = self.tm_db.lookup_entry("Repeat", "en", "es")
        
        time.sleep(0.01) # Ensure time difference
        self.tm_db.add_entry("Repeat", "Repetir_v2_higher_conf", "en", "es", confidence=0.9)
        _, entry_id_v2_conf = self.tm_db.lookup_entry("Repeat", "en", "es")
        
        # v2 should be returned due to higher confidence (and later creation implicitly means later last_used_at initially)
        self.assertEqual(self.tm_db.lookup_entry("Repeat", "en", "es")[0], "Repetir_v2_higher_conf")

        time.sleep(0.01)
        # Now update v1 to be used more recently
        self.tm_db.update_last_used(entry_id_v1)
        
        # v1 should now be returned as it was used more recently, despite lower confidence
        # This assumes last_used_at DESC takes precedence over confidence DESC in ORDER BY
        self.assertEqual(self.tm_db.lookup_entry("Repeat", "en", "es")[0], "Repetir_v1")

if __name__ == '__main__':
    unittest.main()
