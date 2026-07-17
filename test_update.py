import unittest
import os
import json
import tempfile
import datetime
from update import ProfileStatusManager

class TestProfileStatusManager(unittest.TestCase):
    def setUp(self):
        # Create temporary files for isolated testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.readme_path = os.path.join(self.temp_dir.name, "README.md")
        self.tips_path = os.path.join(self.temp_dir.name, "tips.json")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_get_daily_tip_fallback_when_missing(self):
        # When file is missing, should return DEFAULT_TIP
        manager = ProfileStatusManager(self.readme_path, self.tips_path)
        tip = manager.get_daily_tip()
        self.assertEqual(tip, ProfileStatusManager.DEFAULT_TIP)

    def test_get_daily_tip_fallback_when_empty(self):
        # When file is empty or has empty list, should return DEFAULT_TIP
        with open(self.tips_path, "w", encoding="utf-8") as f:
            json.dump({"tips": []}, f)

        manager = ProfileStatusManager(self.readme_path, self.tips_path)
        tip = manager.get_daily_tip()
        self.assertEqual(tip, ProfileStatusManager.DEFAULT_TIP)

    def test_get_daily_tip_rotation(self):
        # When valid file is present, should return one of the tips
        mock_tips = ["Tip A", "Tip B", "Tip C"]
        with open(self.tips_path, "w", encoding="utf-8") as f:
            json.dump({"tips": mock_tips}, f)

        manager = ProfileStatusManager(self.readme_path, self.tips_path)
        tip = manager.get_daily_tip()
        self.assertIn(tip, mock_tips)

    def test_generate_status_section(self):
        manager = ProfileStatusManager(self.readme_path, self.tips_path)
        timestamp = "2026-07-17 09:00:00 UTC"
        tip = "Mock Tip"
        section = manager.generate_status_section(tip, timestamp)

        self.assertIn(ProfileStatusManager.START_MARKER, section)
        self.assertIn(ProfileStatusManager.END_MARKER, section)
        self.assertIn(timestamp, section)
        self.assertIn(tip, section)

    def test_update_readme_success(self):
        # Set up a mock README and tips file
        initial_readme = (
            "# My Profile\n"
            "<!-- SYSTEM_STATUS_START -->\n"
            "old status\n"
            "<!-- SYSTEM_STATUS_END -->\n"
            "Footer info\n"
        )
        with open(self.readme_path, "w", encoding="utf-8") as f:
            f.write(initial_readme)

        mock_tips = ["Awesome ML Tip"]
        with open(self.tips_path, "w", encoding="utf-8") as f:
            json.dump({"tips": mock_tips}, f)

        manager = ProfileStatusManager(self.readme_path, self.tips_path)
        updated = manager.update_readme()

        self.assertTrue(updated)

        with open(self.readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("Awesome ML Tip", content)
        self.assertIn("Last Synchronized", content)
        self.assertNotIn("old status", content)

    def test_update_readme_missing_markers(self):
        # No markers in README
        initial_readme = "# My Profile\nNo markers here\n"
        with open(self.readme_path, "w", encoding="utf-8") as f:
            f.write(initial_readme)

        manager = ProfileStatusManager(self.readme_path, self.tips_path)
        updated = manager.update_readme()

        self.assertFalse(updated)

if __name__ == "__main__":
    unittest.main()
