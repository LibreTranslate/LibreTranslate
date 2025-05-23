import unittest
import json
import time
from libretranslate.app import app, tm_db # Assuming tm_db is accessible for direct manipulation
from libretranslate.tm_db import TMDatabase # To potentially re-init tm_db with a test db

class TestApiTranslateTM(unittest.TestCase):

    def setUp(self):
        # Configure the app for testing
        app.config['TESTING'] = True
        # Use an in-memory SQLite database for TM for these tests
        # This requires ensuring the tm_db instance in app.py uses this path during tests
        # A cleaner way might be to allow app creation with a specific TM db path
        # For now, let's assume tm_db can be re-pointed or is already using :memory: for tests
        
        # If tm_db is already initialized by app.py, we might need to clear its tables
        # or ensure it's using a dedicated test database.
        # The ideal way is to pass a test tm_db_path to create_app, if create_app supports it.
        # If not, we can try to re-initialize the tm_db instance if it's globally accessible.
        
        # Let's assume tm_db is initialized in app.py and accessible.
        # We will clear its content before each test for isolation.
        # Or, even better, if tm_db is None when no api_keys, we can set it here.
        
        # This is a bit of a hack. Ideally, app factory should handle test DBs.
        # Forcing app.tm_db to a new in-memory instance for each test run in this suite.
        # This assumes 'tm_db' is an attribute of 'app' or can be globally replaced.
        # If app.py's tm_db is initialized like `tm_db = TMDatabase()`, this is tricky.
        # Let's assume we can access and clear the tm_db from the imported app.
        
        # Resetting the global tm_db instance in the app module for true isolation
        global tm_db
        self.original_tm_db_path = TMDatabase().db_path # Store original path if any
        tm_db = TMDatabase(db_path=":memory:") # Override with in-memory for tests
        app.tm_db = tm_db # If the app instance uses an attribute

        self.client = app.test_client()

        # Clear all entries from tm_db before each test
        with tm_db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM translation_memory")
            conn.commit()

    def tearDown(self):
        # Restore original tm_db if needed, or ensure cleanup
        # If we overrode a global tm_db, restore it or handle as per app structure
        # For now, the in-memory DB will be gone. If it was file-based, delete it.
        # If we overrode a global, it might be better to have a test app instance.
        pass

    def test_1_translate_save_to_tm(self):
        """Test that a new translation is saved to TM."""
        payload = {
            "q": "New text to translate",
            "source": "en",
            "target": "es"
        }
        response = self.client.post('/translate', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIn("translatedText", data)
        self.assertIn("retrieved_from_tm", data)
        self.assertFalse(data["retrieved_from_tm"])
        translated_text = data["translatedText"]

        # Verify in DB (using the app's tm_db instance)
        time.sleep(0.01) # Allow async write if any, though SQLite typically isn't
        tm_entry = tm_db.lookup_entry("New text to translate", "en", "es")
        self.assertIsNotNone(tm_entry)
        self.assertEqual(tm_entry[0], translated_text)

    def test_2_translate_from_tm(self):
        """Test that a translation is retrieved from TM if it exists."""
        # Add an entry first
        source_text = "Text already in TM"
        target_text_manual = "Texto ya en TM"
        tm_db.add_entry(source_text, target_text_manual, "en", "es")

        # Get the initial last_used_at time
        _, entry_id = tm_db.lookup_entry(source_text, "en", "es")
        with tm_db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT last_used_at FROM translation_memory WHERE id=?", (entry_id,))
            timestamp_before_str = cursor.fetchone()["last_used_at"]
        timestamp_before = time.mktime(time.strptime(timestamp_before_str, "%Y-%m-%d %H:%M:%S"))

        time.sleep(0.01) # Ensure a time difference for last_used_at update check

        payload = {
            "q": source_text,
            "source": "en",
            "target": "es"
        }
        response = self.client.post('/translate', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)

        self.assertEqual(data["translatedText"], target_text_manual)
        self.assertTrue(data["retrieved_from_tm"])

        # Verify last_used_at was updated
        with tm_db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT last_used_at FROM translation_memory WHERE id=?", (entry_id,))
            timestamp_after_str = cursor.fetchone()["last_used_at"]
        timestamp_after = time.mktime(time.strptime(timestamp_after_str, "%Y-%m-%d %H:%M:%S"))
        
        self.assertGreater(timestamp_after, timestamp_before)

    def test_3_translate_batch_tm(self):
        """Test batch translation with mixed TM and non-TM items."""
        # Item 1: Will be in TM
        tm_db.add_entry("Hello from batch", "Hola desde lote", "en", "es")
        # Item 2: Will not be in TM, will be translated
        # Item 3: Will be in TM
        tm_db.add_entry("Goodbye from batch", "Adiós desde lote", "en", "es")

        payload = {
            "q": ["Hello from batch", "New text for batch", "Goodbye from batch"],
            "source": "en",
            "target": "es"
        }
        response = self.client.post('/translate', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)

        self.assertIsInstance(data["translatedText"], list)
        self.assertEqual(len(data["translatedText"]), 3)
        
        # Since one item ("New text for batch") was not in TM, the whole batch is translated,
        # so retrieved_from_tm should be False for the batch response.
        # The current app.py logic: if any part of batch needs translation, whole batch is translated and retrieved_from_tm is false.
        # If all from TM, then retrieved_from_tm is true.
        # Let's test the "all from TM" case first, then the "mixed" case which results in full translation.

        # Case 3a: All items from TM
        payload_all_tm = {
            "q": ["Hello from batch", "Goodbye from batch"],
            "source": "en",
            "target": "es"
        }
        response_all_tm = self.client.post('/translate', data=json.dumps(payload_all_tm), content_type='application/json')
        self.assertEqual(response_all_tm.status_code, 200)
        data_all_tm = json.loads(response_all_tm.data)
        self.assertTrue(data_all_tm["retrieved_from_tm"])
        self.assertEqual(data_all_tm["translatedText"][0], "Hola desde lote")
        self.assertEqual(data_all_tm["translatedText"][1], "Adiós desde lote")


        # Case 3b: Mixed items (results in full translation, TM save for new items)
        response_mixed = self.client.post('/translate', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response_mixed.status_code, 200)
        data_mixed = json.loads(response_mixed.data)

        self.assertFalse(data_mixed["retrieved_from_tm"]) 
        # Check specific translations (Hola and Adiós might be re-translated by the model, but should be consistent)
        self.assertEqual(data_mixed["translatedText"][0], "Hola desde lote") # Assuming model gives same as TM for existing
        # self.assertNotEqual(data_mixed["translatedText"][1], "New text for batch") # Should be translated
        self.assertTrue(len(data_mixed["translatedText"][1]) > 0)
        self.assertEqual(data_mixed["translatedText"][2], "Adiós desde lote") # Assuming model gives same as TM

        # Verify "New text for batch" was saved to TM
        time.sleep(0.01)
        new_entry_lookup = tm_db.lookup_entry("New text for batch", "en", "es")
        self.assertIsNotNone(new_entry_lookup)
        self.assertEqual(new_entry_lookup[0], data_mixed["translatedText"][1])

    def test_4_translate_auto_source_save_to_tm(self):
        """Test that translation with source 'auto' still saves to TM with detected lang."""
        payload = {
            "q": "This is English text", # Clearly English
            "source": "auto",
            "target": "fr" # Translate to French
        }
        response = self.client.post('/translate', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)

        self.assertFalse(data["retrieved_from_tm"])
        self.assertIn("detectedLanguage", data)
        self.assertEqual(data["detectedLanguage"]["language"], "en") # Expect 'en' model code
        
        translated_text = data["translatedText"]

        # Verify in DB with detected source language 'en'
        time.sleep(0.01)
        tm_entry = tm_db.lookup_entry("This is English text", "en", "fr")
        self.assertIsNotNone(tm_entry)
        self.assertEqual(tm_entry[0], translated_text)

    def test_5_translate_from_tm_respects_target_lang(self):
        """Test TM lookup considers the target language."""
        tm_db.add_entry("Hello", "Hola", "en", "es")
        tm_db.add_entry("Hello", "Bonjour", "en", "fr")

        # Request translation to Spanish
        payload_es = {"q": "Hello", "source": "en", "target": "es"}
        response_es = self.client.post('/translate', data=json.dumps(payload_es), content_type='application/json')
        data_es = json.loads(response_es.data)
        self.assertTrue(data_es["retrieved_from_tm"])
        self.assertEqual(data_es["translatedText"], "Hola")

        # Request translation to French
        payload_fr = {"q": "Hello", "source": "en", "target": "fr"}
        response_fr = self.client.post('/translate', data=json.dumps(payload_fr), content_type='application/json')
        data_fr = json.loads(response_fr.data)
        self.assertTrue(data_fr["retrieved_from_tm"])
        self.assertEqual(data_fr["translatedText"], "Bonjour")


if __name__ == '__main__':
    unittest.main()
