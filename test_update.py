import unittest
from unittest.mock import patch, mock_open
import datetime
import os

from update import ProfileStatusManager

class TestProfileStatusManager(unittest.TestCase):
    def setUp(self):
        self.readme_path = "dummy_readme.md"
        self.tips_path = "dummy_tips.json"
        self.manager = ProfileStatusManager(self.readme_path, self.tips_path)

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data='{"tips": ["Tip 1", "Tip 2"]}')
    def test_get_daily_tip_success(self, mock_file, mock_exists):
        mock_exists.return_value = True

        real_now = datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc)  # tm_yday = 1
        with patch("update.datetime.datetime") as mock_datetime_class:
            mock_datetime_class.now.return_value = real_now

            tip = self.manager.get_daily_tip()
            # 1 % 2 = 1 -> "Tip 2"
            self.assertEqual(tip, "Tip 2")

    @patch("os.path.exists")
    def test_get_daily_tip_missing_file_fallback(self, mock_exists):
        mock_exists.return_value = False
        tip = self.manager.get_daily_tip()
        self.assertEqual(tip, ProfileStatusManager.DEFAULT_TIP)

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data='{"tips": []}')
    def test_get_daily_tip_empty_list_fallback(self, mock_file, mock_exists):
        mock_exists.return_value = True
        tip = self.manager.get_daily_tip()
        self.assertEqual(tip, ProfileStatusManager.DEFAULT_TIP)

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data='invalid json')
    def test_get_daily_tip_corrupted_json_fallback(self, mock_file, mock_exists):
        mock_exists.return_value = True
        tip = self.manager.get_daily_tip()
        self.assertEqual(tip, ProfileStatusManager.DEFAULT_TIP)

    def test_generate_status_section(self):
        tip = "Stay clean."
        timestamp = "2026-07-19 09:08:00 UTC"
        section = self.manager.generate_status_section(tip, timestamp)

        self.assertIn(ProfileStatusManager.START_MARKER, section)
        self.assertIn(ProfileStatusManager.END_MARKER, section)
        self.assertIn(tip, section)
        self.assertIn(timestamp, section)

    @patch("os.path.exists")
    @patch("update.ProfileStatusManager.get_daily_tip")
    @patch("builtins.open", new_callable=mock_open, read_data="prefix\n<!-- SYSTEM_STATUS_START -->\nold\n<!-- SYSTEM_STATUS_END -->\nsuffix")
    def test_update_readme_success(self, mock_file, mock_tip, mock_exists):
        mock_exists.return_value = True
        mock_tip.return_value = "New Tip"

        # Call update_readme
        result = self.manager.update_readme()
        self.assertTrue(result)

        # Check that it was opened for writing and written to
        mock_file.assert_any_call(self.manager.readme_path, "w", encoding="utf-8")

        # Verify the write content contains the new tip
        handle = mock_file()
        written_content = "".join([call.args[0] for call in handle.write.call_args_list])
        self.assertIn("New Tip", written_content)
        self.assertIn("prefix", written_content)
        self.assertIn("suffix", written_content)

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data="no markers here")
    def test_update_readme_missing_markers(self, mock_file, mock_exists):
        mock_exists.return_value = True
        result = self.manager.update_readme()
        self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()
