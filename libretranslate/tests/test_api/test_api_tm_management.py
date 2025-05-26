import unittest
import json
from libretranslate.app import app, tm_db # Assuming tm_db is accessible
from libretranslate.tm_db import TMDatabase # For re-init or type hinting

class TestApiTmManagement(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        
        # Similar to TestApiTranslateTM, ensuring a clean TM for each test.
        # This assumes tm_db in app.py can be effectively managed for tests.
        global tm_db 
        # If tm_db was initialized with a file, this :memory: override is crucial.
        # If tm_db is a module-level variable in app.py, this override works.
        # If tm_db is instance variable of app, then app.tm_db = ...
        # For now, assuming global tm_db in app module or app.tm_db works.
        tm_db_instance = TMDatabase(db_path=":memory:") # Create a new in-memory DB instance
        
        # This part is tricky if tm_db is not easily replaceable in the 'app' context.
        # If 'app.tm_db' is the way the app accesses it:
        app.tm_db = tm_db_instance 
        # If 'tm_db' is a global in the module 'app' uses:
        # For this to work, the 'tm_db' in 'from libretranslate.app import app, tm_db'
        # must be the same instance the app routes will use.
        # A common pattern is to have `app.extensions['tm_db'] = tm_db_instance`
        # or `app.tm_db = tm_db_instance`.
        # Let's proceed assuming app.tm_db or a global tm_db that routes use is now :memory:
        
        self.client = app.test_client()
        self.tm_db_instance = app.tm_db # Use the same instance the app is using

        # Clear all entries from tm_db before each test
        with self.tm_db_instance._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM translation_memory")
            conn.commit()

    def tearDown(self):
        pass # In-memory DB is cleared automatically

    def test_1_add_tm_entry_success(self):
        """Test successful creation of a new TM entry via API."""
        payload = {
            "source_text": "Hello API",
            "target_text": "Hola API",
            "source_lang": "en", # ISO code
            "target_lang": "es", # ISO code
            "user_id": 123,
            "confidence": 0.85
        }
        response = self.client.post('/tm/entries', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 201, f"Response data: {response.data.decode()}")
        data = json.loads(response.data)
        self.assertEqual(data["message"], "TM entry added successfully")

        # Verify in DB (using model codes)
        entries, count = self.tm_db_instance.list_entries(source_lang="en", target_lang="es")
        self.assertEqual(count, 1)
        self.assertEqual(entries[0]["source_text"], "Hello API")
        self.assertEqual(entries[0]["target_text"], "Hola API")
        self.assertEqual(entries[0]["user_id"], 123)
        self.assertEqual(entries[0]["confidence"], 0.85)

    def test_2_add_tm_entry_missing_fields(self):
        """Test TM entry creation with missing required fields."""
        payload = {
            "source_text": "Incomplete",
            # target_text is missing
            "source_lang": "en",
            "target_lang": "de"
        }
        response = self.client.post('/tm/entries', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertIn("Missing required fields", data["error"])

    def test_3_add_tm_entry_invalid_lang_codes(self):
        """Test TM entry creation with invalid language codes."""
        payload = {
            "source_text": "Text",
            "target_text": "Texto",
            "source_lang": "invalidlang", # Invalid ISO
            "target_lang": "es"
        }
        response = self.client.post('/tm/entries', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400) # iso2model should handle this
        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertIn("Invalid source_lang or target_lang", data["error"])

    def test_4_list_tm_entries_basic_and_pagination(self):
        """Test listing TM entries and pagination."""
        for i in range(15): # Add 15 entries
            self.tm_db_instance.add_entry(f"Src {i}", f"Tgt {i}", "en", "pl", user_id=i)

        # Get first page (default per_page is 20, so all 15 should be there)
        response_p1 = self.client.get('/tm/entries?page=1&per_page=10')
        self.assertEqual(response_p1.status_code, 200)
        data_p1 = json.loads(response_p1.data)
        self.assertEqual(len(data_p1["entries"]), 10)
        self.assertEqual(data_p1["total_entries"], 15)
        self.assertEqual(data_p1["page"], 1)
        self.assertEqual(data_p1["per_page"], 10)
        self.assertEqual(data_p1["entries"][0]["source_text"], "Src 14") # Ordered by ID DESC

        # Get second page
        response_p2 = self.client.get('/tm/entries?page=2&per_page=10')
        self.assertEqual(response_p2.status_code, 200)
        data_p2 = json.loads(response_p2.data)
        self.assertEqual(len(data_p2["entries"]), 5) # Remaining 5
        self.assertEqual(data_p2["entries"][0]["source_text"], "Src 4")

    def test_5_list_tm_entries_filtered(self):
        """Test filtering TM entries by source and target languages."""
        self.tm_db_instance.add_entry("Eng-Spa", "English to Spanish", "en", "es")
        self.tm_db_instance.add_entry("Eng-Fra", "English to French", "en", "fr")
        self.tm_db_instance.add_entry("Fra-Eng", "French to English", "fr", "en")

        # Filter by source_lang=en (ISO)
        response_src_en = self.client.get('/tm/entries?source_lang=en')
        data_src_en = json.loads(response_src_en.data)
        self.assertEqual(response_src_en.status_code, 200)
        self.assertEqual(data_src_en["total_entries"], 2)
        # Check if returned entries indeed have source_lang 'en'
        for entry in data_src_en["entries"]:
            self.assertEqual(entry["source_lang"], "en")

        # Filter by target_lang=es (ISO)
        response_tgt_es = self.client.get('/tm/entries?target_lang=es')
        data_tgt_es = json.loads(response_tgt_es.data)
        self.assertEqual(response_tgt_es.status_code, 200)
        self.assertEqual(data_tgt_es["total_entries"], 1)
        self.assertEqual(data_tgt_es["entries"][0]["source_text"], "Eng-Spa")

        # Filter by source_lang=en and target_lang=fr
        response_en_fr = self.client.get('/tm/entries?source_lang=en&target_lang=fr')
        data_en_fr = json.loads(response_en_fr.data)
        self.assertEqual(response_en_fr.status_code, 200)
        self.assertEqual(data_en_fr["total_entries"], 1)
        self.assertEqual(data_en_fr["entries"][0]["source_text"], "Eng-Fra")

    def test_6_delete_tm_entry_success(self):
        """Test successful deletion of a TM entry."""
        self.tm_db_instance.add_entry("To Delete", "Para Borrar", "en", "es")
        entries_before, _ = self.tm_db_instance.list_entries(source_lang="en", target_lang="es")
        entry_id_to_delete = entries_before[0]["id"]

        response = self.client.delete(f'/tm/entries/{entry_id_to_delete}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])

        # Verify entry is gone
        deleted_entry = self.tm_db_instance.get_entry_by_id(entry_id_to_delete)
        self.assertIsNone(deleted_entry)

    def test_7_delete_tm_entry_not_found(self):
        """Test deleting a non-existent TM entry."""
        response = self.client.delete('/tm/entries/99999') # Non-existent ID
        self.assertEqual(response.status_code, 404) # As per current implementation
        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertIn("TM entry not found or could not be deleted", data["error"])

if __name__ == '__main__':
    unittest.main()
