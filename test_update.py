#!/usr/bin/env python3
"""
test_update.py - Unit test suite for verifying update.py functionality, edge cases,
and file operations in isolation.
"""

import os
import json
import unittest
import tempfile
from datetime import datetime
from update import ProfileStatusManager


class TestProfileStatusManager(unittest.TestCase):
    """Unit tests for the ProfileStatusManager class."""

    def setUp(self):
        # Create a temporary directory for isolated test environment
        self.test_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.test_dir.cleanup)

        # Define paths within the temporary directory
        self.data_dir = os.path.join(self.test_dir.name, "data")
        os.makedirs(self.data_dir, exist_ok=True)

        self.tips_file_path = os.path.join(self.data_dir, "tips.json")
        self.readme_path = os.path.join(self.test_dir.name, "README.md")

        # Instantiate manager pointing to the temporary directory
        self.manager = ProfileStatusManager(base_dir=self.test_dir.name)

    def write_tips(self, tips_list):
        """Helper to write the mock tips list to the temporary file."""
        with open(self.tips_file_path, "w", encoding="utf-8") as f:
            json.dump(tips_list, f)

    def write_readme(self, content):
        """Helper to write mockup content to README.md."""
        with open(self.readme_path, "w", encoding="utf-8") as f:
            f.write(content)

    def test_get_daily_tip_with_valid_data(self):
        """Verify daily tip rotation logic with valid tips."""
        mock_tips = ["Tip A", "Tip B", "Tip C"]
        self.write_tips(mock_tips)

        # Use datetime day-of-year rotation
        day_of_year = datetime.utcnow().timetuple().tm_yday
        expected_tip = mock_tips[day_of_year % len(mock_tips)]

        actual_tip = self.manager.get_daily_tip()
        self.assertEqual(actual_tip, expected_tip)

    def test_get_daily_tip_fallback_when_file_missing(self):
        """Verify fallback when tips.json does not exist."""
        # Intentionally do not write the file
        actual_tip = self.manager.get_daily_tip()
        self.assertEqual(actual_tip, self.manager.DEFAULT_TIP)

    def test_get_daily_tip_fallback_when_file_empty(self):
        """Verify fallback when tips.json is empty or invalid JSON."""
        with open(self.tips_file_path, "w", encoding="utf-8") as f:
            f.write("[]")  # Empty array

        actual_tip = self.manager.get_daily_tip()
        self.assertEqual(actual_tip, self.manager.DEFAULT_TIP)

    def test_get_daily_tip_fallback_when_invalid_json(self):
        """Verify fallback when tips.json contains invalid JSON syntax."""
        with open(self.tips_file_path, "w", encoding="utf-8") as f:
            f.write("invalid json content")

        actual_tip = self.manager.get_daily_tip()
        self.assertEqual(actual_tip, self.manager.DEFAULT_TIP)

    def test_generate_status_section_format(self):
        """Verify correct markdown table structure and parameters inside status section."""
        tip = "Never stop learning."
        timestamp = "2026-07-21 12:30:00 UTC"
        section = self.manager.generate_status_section(tip, timestamp)

        self.assertIn("### ⚙️ SYSTEM STATUS", section)
        self.assertIn(timestamp, section)
        self.assertIn(tip, section)
        self.assertIn("| **Last Automated Sync** | 🟢 Online |", section)

    def test_update_readme_success(self):
        """Verify full replacement flow when README contains correct markers."""
        self.write_tips(["Keep it simple."])
        initial_content = (
            "Hello World!\n"
            "<!-- SYSTEM_STATUS_START -->\n"
            "<!-- SYSTEM_STATUS_END -->\n"
            "Footer here."
        )
        self.write_readme(initial_content)

        success = self.manager.update_readme()
        self.assertTrue(success)

        # Read updated README
        with open(self.readme_path, "r", encoding="utf-8") as f:
            updated_content = f.read()

        self.assertIn("### ⚙️ SYSTEM STATUS", updated_content)
        self.assertIn("Keep it simple.", updated_content)
        self.assertIn("<!-- SYSTEM_STATUS_START -->", updated_content)
        self.assertIn("<!-- SYSTEM_STATUS_END -->", updated_content)

    def test_update_readme_missing_markers(self):
        """Verify error handling / graceful failure when markers are missing."""
        initial_content = "Hello World! No markers here."
        self.write_readme(initial_content)

        success = self.manager.update_readme()
        self.assertFalse(success)

    def test_update_readme_no_changes(self):
        """Verify return code when there is no change to apply (consecutive runs)."""
        self.write_tips(["Keep it simple."])
        initial_content = (
            "Hello World!\n"
            "<!-- SYSTEM_STATUS_START -->\n"
            "<!-- SYSTEM_STATUS_END -->\n"
            "Footer here."
        )
        self.write_readme(initial_content)

        # First update to initialize
        first_success = self.manager.update_readme()
        self.assertTrue(first_success)

        # Mock current_time within manager or simulate consecutive run with identical content
        # Because timestamp has seconds granularity, if we run immediately, it might have the same value,
        # but to guarantee identical content, we can manually freeze or replace timestamp.
        # Alternatively, we read and rewrite with the same exact timestamp:
        with open(self.readme_path, "r", encoding="utf-8") as f:
            first_updated = f.read()

        # Mock datetime to return exactly the same string or rely on fast execution.
        # Let's mock datetime inside update module for precise comparison:
        import update
        original_datetime = update.datetime

        class MockedDatetime:
            @classmethod
            def utcnow(cls):
                # Always returns a fixed date/time
                return datetime(2026, 7, 21, 12, 30, 0)

        try:
            update.datetime = MockedDatetime
            # First run under mocked datetime
            self.write_readme(initial_content)
            self.manager.update_readme()

            # Second run with same mocked datetime should not rewrite
            second_success = self.manager.update_readme()
            self.assertFalse(second_success)
        finally:
            update.datetime = original_datetime


if __name__ == "__main__":
    unittest.main()
