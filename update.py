import json
import datetime
import os
import logging
from typing import List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class ProfileStatusManager:
    """Manages the synchronization of README content with system status and tips."""

    DEFAULT_TIP = "Stay curious and keep coding!"
    START_MARKER = '<!-- SYSTEM_STATUS_START -->'
    END_MARKER = '<!-- SYSTEM_STATUS_END -->'

    def __init__(self, readme_path: str, tips_path: str):
        self.readme_path = os.path.abspath(readme_path)
        self.tips_path = os.path.abspath(tips_path)

    def get_daily_tip(self) -> str:
        """Fetches a daily tip from the tips database using a UTC day-of-year index."""
        try:
            if not os.path.exists(self.tips_path):
                logger.warning(f"Tips file not found at {self.tips_path}. Using fallback.")
                return self.DEFAULT_TIP

            with open(self.tips_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            tips: List[str] = data.get('tips', [])
            if not tips:
                logger.warning("No tips found in database. Using fallback.")
                return self.DEFAULT_TIP

            # Use day of the year in UTC to select a tip consistently
            day_of_year = datetime.datetime.now(datetime.timezone.utc).timetuple().tm_yday
            selected_tip = tips[day_of_year % len(tips)]
            return selected_tip

        except Exception as e:
            logger.error(f"Error fetching tip: {e}")
            return self.DEFAULT_TIP

    def generate_status_section(self, tip: str, timestamp: str) -> str:
        """Generates the formatted status section for the README."""
        return (
            f"{self.START_MARKER}\n"
            f"| 🛰️ Status | 🟢 Operational |\n"
            f"| :--- | :--- |\n"
            f"| **Last Synchronized** | `{timestamp}` |\n"
            f"| **Tactical Tip** | `{tip}` |\n"
            f"{self.END_MARKER}"
        )

    def update_readme(self) -> bool:
        """Updates the README.md file with the latest system status."""
        try:
            if not os.path.exists(self.readme_path):
                logger.error(f"README.md not found at {self.readme_path}")
                return False

            tip = self.get_daily_tip()
            current_time = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

            with open(self.readme_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if self.START_MARKER not in content or self.END_MARKER not in content:
                logger.error("System status markers not found in README.md")
                return False

            status_section = self.generate_status_section(tip, current_time)

            # Find markers and replace content
            start_idx = content.find(self.START_MARKER)
            end_idx = content.find(self.END_MARKER) + len(self.END_MARKER)

            new_content = content[:start_idx] + status_section + content[end_idx:]

            if new_content == content:
                logger.info("No changes detected in README.md content.")
                return False

            with open(self.readme_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            logger.info(f"README successfully updated with tip: {tip}")
            return True

        except Exception as e:
            logger.error(f"Critical error during README update: {e}")
            return False

if __name__ == "__main__":
    # Path resolution
    base_dir = os.path.dirname(os.path.abspath(__file__))
    readme_file = os.path.join(base_dir, 'README.md')
    tips_file = os.path.join(base_dir, 'data', 'tips.json')

    manager = ProfileStatusManager(readme_file, tips_file)
    manager.update_readme()
