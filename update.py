import json
import datetime
import os
import logging
from typing import List, Optional

# Configure logging with clear, professional output formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class ProfileStatusManager:
    """
    Manages the automated synchronization of the GitHub Profile README.

    This includes:
    - Daily tip rotation based on UTC day-of-year index.
    - Synchronizing the operational status and timestamp.
    - Safe marker-based content replacement.
    """

    DEFAULT_TIP: str = "Stay curious and keep coding!"
    START_MARKER: str = '<!-- SYSTEM_STATUS_START -->'
    END_MARKER: str = '<!-- SYSTEM_STATUS_END -->'

    def __init__(self, readme_path: str, tips_path: str) -> None:
        self.readme_path = os.path.abspath(readme_path)
        self.tips_path = os.path.abspath(tips_path)

    def get_daily_tip(self) -> str:
        """
        Retrieves a deterministic daily tip from the JSON database.
        Uses UTC day-of-year index to ensure global consistency across timezones.
        """
        try:
            if not os.path.exists(self.tips_path):
                logger.warning(f"Tips database file not found at: {self.tips_path}. Using fallback.")
                return self.DEFAULT_TIP

            with open(self.tips_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            tips: List[str] = data.get('tips', [])
            if not tips:
                logger.warning("Tips list is empty in the database. Using fallback.")
                return self.DEFAULT_TIP

            # Ensure UTC consistency
            now = datetime.datetime.now(datetime.timezone.utc)
            day_index = now.timetuple().tm_yday

            selected_tip = tips[day_index % len(tips)]
            return selected_tip
        except Exception as e:
            logger.error(f"Error while retrieving daily tip: {e}. Falling back.")
            return self.DEFAULT_TIP

    def generate_status_section(self, tip: str, timestamp: str) -> str:
        """Constructs the formatted markdown table for the README status section."""
        return (
            f"{self.START_MARKER}\n"
            f"| 🛰️ Status | 🟢 Operational |\n"
            f"| :--- | :--- |\n"
            f"| **Last Synchronized** | `{timestamp}` |\n"
            f"| **Tactical Tip** | `{tip}` |\n"
            f"{self.END_MARKER}"
        )

    def update_readme(self) -> bool:
        """
        Updates the README.md file with the latest status table.
        Performs in-place updates only if changes are detected to avoid redundant writes.
        """
        try:
            if not os.path.exists(self.readme_path):
                logger.error(f"README.md file not found at: {self.readme_path}. Aborting update.")
                return False

            tip = self.get_daily_tip()
            current_time = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

            with open(self.readme_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if self.START_MARKER not in content or self.END_MARKER not in content:
                logger.error("Required SYSTEM_STATUS markers are missing from README.md.")
                return False

            status_section = self.generate_status_section(tip, current_time)

            # Find marker indices
            start_idx = content.find(self.START_MARKER)
            end_idx = content.find(self.END_MARKER) + len(self.END_MARKER)

            # Replace block
            new_content = content[:start_idx] + status_section + content[end_idx:]

            if new_content == content:
                logger.info("No modifications detected. README is already up to date.")
                return False

            with open(self.readme_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            logger.info(f"Successfully synchronized README.md status at {current_time}.")
            return True

        except Exception as e:
            logger.error(f"Unexpected error while updating README.md: {e}")
            return False

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    README_FILE = os.path.join(BASE_DIR, 'README.md')
    TIPS_FILE = os.path.join(BASE_DIR, 'data', 'tips.json')

    manager = ProfileStatusManager(README_FILE, TIPS_FILE)
    manager.update_readme()
