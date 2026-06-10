import json
import datetime
import os
import logging
from typing import List

# Configure logging to provide visibility into the update process

# Configure logging to provide clear, actionable output during CI execution

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class ProfileStatusManager:

    """Manages the synchronization of README content with system status and tactical tips."""

    """
    Manages the automated synchronization of the GitHub Profile README.

    Handles:
    - Daily tip rotation based on UTC day-of-year index.
    - Timestamp synchronization for system status.
    - Content replacement using targeted markers.
    """

    DEFAULT_TIP = "Stay curious and keep coding!"
    START_MARKER = '<!-- SYSTEM_STATUS_START -->'
    END_MARKER = '<!-- SYSTEM_STATUS_END -->'

    def __init__(self, readme_path: str, tips_path: str):
        self.readme_path = os.path.abspath(readme_path)
        self.tips_path = os.path.abspath(tips_path)

    def get_daily_tip(self) -> str:
        """

        Fetches a daily tip from the tips database using a UTC day-of-year index.
        This ensures that every user sees the same tip on a given day, regardless of when the script runs.
        """
        try:
            if not os.path.exists(self.tips_path):
                logger.warning(f"Tips database not found at {self.tips_path}. Using fallback.")

        Retrieves a deterministic daily tip from the JSON database.
        Uses UTC date to ensure all visitors see the same tip globally.
        """
        try:
            if not os.path.exists(self.tips_path):
                logger.warning(f"Tips database missing at {self.tips_path}. Falling back to default.")

                return self.DEFAULT_TIP

            with open(self.tips_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            tips: List[str] = data.get('tips', [])
            if not tips:
                logger.warning("Empty tips database. Falling back to default.")
                return self.DEFAULT_TIP


            # Use UTC date to ensure global consistency
            now = datetime.datetime.now(datetime.timezone.utc)
            day_index = now.timetuple().tm_yday

            # Deterministic selection based on the day of the year

            # Select tip based on UTC day of the year
            now = datetime.datetime.now(datetime.timezone.utc)
            day_index = now.timetuple().tm_yday

            # Deterministic selection based on day of the year

            return tips[day_index % len(tips)]
        except Exception as e:
            logger.error(f"Unexpected error retrieving tip: {e}")
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

        Updates the README.md file with the latest system status and tip.
        Returns True if the file was modified, False otherwise.

        Performs the README update. Only writes to disk if content has changed
        to prevent redundant commits in the repository.

        """
        try:
            if not os.path.exists(self.readme_path):
                logger.error(f"README.md not found at {self.readme_path}. Execution aborted.")
                return False

            tip = self.get_daily_tip()
            current_time = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

            with open(self.readme_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if self.START_MARKER not in content or self.END_MARKER not in content:

                logger.error("System status markers not found in README.md. Please ensure the markers are present.")

                logger.error("Required markers (SYSTEM_STATUS) not found in README.md.")

                return False

            status_section = self.generate_status_section(tip, current_time)

            # Find markers and replace content between them

            # Targeted replacement of the status block

            start_idx = content.find(self.START_MARKER)
            end_idx = content.find(self.END_MARKER) + len(self.END_MARKER)

            new_content = content[:start_idx] + status_section + content[end_idx:]

            # Avoid unnecessary writes if content hasn't changed
            if new_content == content:

                logger.info("README is already up to date. No changes required.")

                logger.info("README content is already up-to-date. No write performed.")

                return False

            with open(self.readme_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            logger.info(f"Successfully synchronized README at {current_time}")

            logger.info(f"README successfully synchronized at {current_time}")

            logger.info(f"Active Tip: {tip}")
            return True

        except Exception as e:
            logger.error(f"Failed to update README: {e}")
            return False

if __name__ == "__main__":

    # Resolve absolute paths relative to this script

    # Define paths relative to the script's location for portability
    base_dir = os.path.dirname(os.path.abspath(__file__))
    readme_file = os.path.join(base_dir, 'README.md')
    tips_file = os.path.join(base_dir, 'data', 'tips.json')
  
    # Internal path resolution relative to the script location

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    README_FILE = os.path.join(BASE_DIR, 'README.md')
    TIPS_FILE = os.path.join(BASE_DIR, 'data', 'tips.json')

    manager = ProfileStatusManager(readme_file, tips_file)
    manager.update_readme()
