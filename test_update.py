import unittest
import os
import tempfile
import json
import datetime
from unittest.mock import patch
from update import ProfileStatusManager

class TestProfileStatusManager(unittest.TestCase):
    def setUp(self):
        # Create temporary files for testing to isolate from live files
        self.temp_readme = tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8')
        self.temp_tips = tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8')

        # Initialize default contents
        self.temp_readme.write(
            "Hello World\n"
            "<!-- SYSTEM_STATUS_START -->\n"
            "| 🛰️ Status | 🟢 Operational |\n"
            "| :--- | :--- |\n"
            "| **Last Synchronized** | `2026-07-19 14:01:24 UTC` |\n"
            "| **Tactical Tip** | `Initial Tip` |\n"
            "<!-- SYSTEM_STATUS_END -->\n"
            "Footer info"
        )
        self.temp_readme.flush()

        self.tips_data = {
            "tips": [
                "Tip A",
                "Tip B",
                "Tip C"
            ]
        }
        json.dump(self.tips_data, self.temp_tips)
        self.temp_tips.flush()

        self.manager = ProfileStatusManager(self.temp_readme.name, self.temp_tips.name)

    def tearDown(self):
        self.temp_readme.close()
        self.temp_tips.close()
        os.unlink(self.temp_readme.name)
        os.unlink(self.temp_tips.name)

    def test_get_daily_tip_success(self):
        # Fix mock time to get a consistent tm_yday
        mock_now = datetime.datetime(2026, 1, 5, 12, 0, 0, tzinfo=datetime.timezone.utc)
        # 2026-01-05 is day 5 of the year
        # 5 % 3 = 2 -> expected "Tip C"
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_now
            tip = self.manager.get_daily_tip()
            self.assertEqual(tip, "Tip C")

    def test_get_daily_tip_missing_file(self):
        bad_manager = ProfileStatusManager(self.temp_readme.name, "non_existent_file.json")
        tip = bad_manager.get_daily_tip()
        self.assertEqual(tip, ProfileStatusManager.DEFAULT_TIP)

    def test_get_daily_tip_empty_file(self):
        # Empty tips list
        with open(self.temp_tips.name, 'w', encoding='utf-8') as f:
            json.dump({"tips": []}, f)
        tip = self.manager.get_daily_tip()
        self.assertEqual(tip, ProfileStatusManager.DEFAULT_TIP)

    def test_get_daily_tip_invalid_json(self):
        with open(self.temp_tips.name, 'w', encoding='utf-8') as f:
            f.write("invalid json")
        tip = self.manager.get_daily_tip()
        self.assertEqual(tip, ProfileStatusManager.DEFAULT_TIP)

    def test_generate_status_section(self):
        tip = "Never stop learning."
        timestamp = "2026-07-20 12:00:00 UTC"
        section = self.manager.generate_status_section(tip, timestamp)

        self.assertIn(ProfileStatusManager.START_MARKER, section)
        self.assertIn(ProfileStatusManager.END_MARKER, section)
        self.assertIn("Never stop learning.", section)
        self.assertIn("2026-07-20 12:00:00 UTC", section)

    def test_update_readme_success(self):
        # Trigger update
        updated = self.manager.update_readme()
        self.assertTrue(updated)

        with open(self.temp_readme.name, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn("Hello World\n", content)
        self.assertIn("Footer info", content)
        self.assertIn("Tactical Tip", content)
        # Should contain one of our tips since it updated
        self.assertTrue(any(t in content for t in self.tips_data["tips"]))

    def test_update_readme_missing_markers(self):
        with open(self.temp_readme.name, 'w', encoding='utf-8') as f:
            f.write("No markers here!")
        updated = self.manager.update_readme()
        self.assertFalse(updated)

    def test_update_readme_missing_file(self):
        bad_manager = ProfileStatusManager("non_existent_readme.md", self.temp_tips.name)
        updated = bad_manager.update_readme()
        self.assertFalse(updated)

if __name__ == '__main__':
    unittest.main()
