#!/usr/bin/env python3
"""
update.py - Automated daily status and tip synchronization engine for Herit Tanna's profile README.
Ensures clean, robust updates to SYSTEM STATUS and Daily Tips.
"""

import os
import json
import logging
from datetime import datetime

# Set up logging with professional formatting
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("ProfileStatusManager")


class ProfileStatusManager:
    """Manages profile README synchronization, status generation, and tip rotation."""

    DEFAULT_TIP = "Stay curious and keep coding!"
    START_MARKER = "<!-- SYSTEM_STATUS_START -->"
    END_MARKER = "<!-- SYSTEM_STATUS_END -->"

    def __init__(self, base_dir=None):
        # Resolve path absolute to script directory to ensure reliability
        if base_dir is None:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))
        else:
            self.base_dir = base_dir

        self.tips_file_path = os.path.join(self.base_dir, "data", "tips.json")
        self.readme_path = os.path.join(self.base_dir, "README.md")

    def get_daily_tip(self) -> str:
        """Rotates a tip from data/tips.json based on the UTC day of the year."""
        if not os.path.exists(self.tips_file_path):
            logger.warning(f"Tips file not found at '{self.tips_file_path}'. Using default tip.")
            return self.DEFAULT_TIP

        try:
            with open(self.tips_file_path, "r", encoding="utf-8") as f:
                tips = json.load(f)

            if not tips or not isinstance(tips, list):
                logger.warning("Tips file is empty or not a list. Using default tip.")
                return self.DEFAULT_TIP

            # Rotation based on UTC day-of-year to ensure daily consistency
            day_of_year = datetime.utcnow().timetuple().tm_yday
            tip_index = day_of_year % len(tips)
            return tips[tip_index]

        except Exception as e:
            logger.error(f"Failed to read/parse tips database: {e}. Using default tip.")
            return self.DEFAULT_TIP

    def generate_status_section(self, tip: str, current_time: str) -> str:
        """Formats the Markdown status section."""
        return (
            f"### ⚙️ SYSTEM STATUS\n\n"
            f"| Metric | Status | Details |\n"
            f"| :--- | :---: | :--- |\n"
            f"| **Last Automated Sync** | 🟢 Online | `{current_time}` |\n"
            f"| **💡 Daily Dev Tip** | 🧠 Active | *\"{tip}\"* |\n"
        )

    def update_readme(self) -> bool:
        """Updates the README.md content with the latest daily status section."""
        if not os.path.exists(self.readme_path):
            logger.error(f"README.md not found at '{self.readme_path}'.")
            return False

        try:
            with open(self.readme_path, "r", encoding="utf-8") as f:
                content = f.read()

            if self.START_MARKER not in content or self.END_MARKER not in content:
                logger.error("Missing system status markers in README.md.")
                return False

            # Get current UTC timestamp and the daily tip
            current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            tip = self.get_daily_tip()

            status_section = self.generate_status_section(tip, current_time)

            # Build updated content
            start_idx = content.find(self.START_MARKER) + len(self.START_MARKER)
            end_idx = content.find(self.END_MARKER)

            before_marker = content[:start_idx]
            after_marker = content[end_idx:]

            new_content = f"{before_marker}\n\n{status_section}\n{after_marker}"

            # Only write if there is a real change to avoid useless commits
            if content == new_content:
                logger.info("README content is already up to date. No write needed.")
                return False

            with open(self.readme_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            logger.info("Successfully updated system status in README.md.")
            return True

        except Exception as e:
            logger.error(f"Failed to update README.md: {e}")
            return False


if __name__ == "__main__":
    manager = ProfileStatusManager()
    manager.update_readme()
