import json
import datetime
import os

from typing import List

class ProfileStatusManager:
    """Manages the automated updates for the GitHub Profile README."""

    def __init__(self, readme_path: str, tips_path: str):
        self.readme_path = readme_path
        self.tips_path = tips_path
        self.start_marker = '<!-- SYSTEM_STATUS_START -->'
        self.end_marker = '<!-- SYSTEM_STATUS_END -->'

    def fetch_daily_tip(self) -> str:
        """Selects a tip from the JSON database using a deterministic daily index."""
        fallback = "Keep exploring, keep learning, and keep coding!"
        try:
            if not os.path.exists(self.tips_path):
                return fallback
import logging
from typing import List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProfileStatusManager:
    """Manages the synchronization of README content and status updates."""

    def __init__(self, readme_path: str, tips_path: str):
        self.readme_path = os.path.abspath(readme_path)
        self.tips_path = os.path.abspath(tips_path)
        self.start_marker = '<!-- SYSTEM_STATUS_START -->'
        self.end_marker = '<!-- SYSTEM_STATUS_END -->'

    def get_daily_tip(self) -> str:
        """Fetches a daily tip from the tips.json file with a fallback mechanism."""
        default_tip = "Stay curious and keep coding!"
        try:
            if not os.path.exists(self.tips_path):
                logger.warning(f"Tips file not found at {self.tips_path}. Using fallback.")
                return default_tip

            with open(self.tips_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            tips: List[str] = data.get('tips', [])
            if not tips:
                return fallback

            # Use UTC date to ensure consistency across all timezones
            now = datetime.datetime.now(datetime.timezone.utc)
            day_index = now.timetuple().tm_yday
            return tips[day_index % len(tips)]
        except Exception as e:
            print(f"Warning: Failed to fetch tip: {e}")
            return fallback

    def update_readme(self) -> bool:
        """Injects the current system status and tactical tip into the README."""
        tip = self.fetch_daily_tip()
        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

        try:
                logger.warning("Tips list is empty. Using fallback.")
                return default_tip

            # Use day of the year in UTC to select a tip consistently
            day_of_year = datetime.datetime.now(datetime.timezone.utc).timetuple().tm_yday
            selected_tip = tips[day_of_year % len(tips)]
            return selected_tip
        except Exception as e:
            logger.error(f"Error fetching tip: {e}")
            return default_tip

    def update_readme(self) -> bool:
        """Updates the README.md file with the latest status and tip."""
        tip = self.get_daily_tip()
        current_time = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

        try:
            if not os.path.exists(self.readme_path):
                logger.error(f"README.md not found at {self.readme_path}")
                return False


            with open(self.readme_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if self.start_marker not in content or self.end_marker not in content:

                print("Error: Required markers missing in README.md")
                return False

            # Construct the new status block
            new_status = (
                f"{self.start_marker}\n"
                f"| 🛰️ Status | 🟢 Operational |\n"
                f"| :--- | :--- |\n"
                f"| **Last Synchronized** | `{timestamp}` |\n"
                logger.error("Status markers not found in README.md")
                return False

            status_section = (
                f"{self.start_marker}\n"
                f"| 🛰️ Status | 🟢 Operational |\n"
                f"| :--- | :--- |\n"
                f"| **Last Synchronized** | `{current_time}` |\n"
                f"| **Tactical Tip** | `{tip}` |\n"
                f"{self.end_marker}"
            )

            # Perform the replacement
            start_pos = content.find(self.start_marker)
            end_pos = content.find(self.end_marker) + len(self.end_marker)
            updated_content = content[:start_pos] + new_status + content[end_pos:]

            if updated_content == content:
                print("Status is already up to date.")
                return False

            with open(self.readme_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)

            print(f"Successfully synchronized profile status at {timestamp}")
            return True

        except Exception as e:
            print(f"Critical Error during README update: {e}")
            return False

if __name__ == "__main__":
    # Resolve absolute paths to ensure reliability in different environments
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    updater = ProfileStatusManager(
        readme_path=os.path.join(ROOT_DIR, 'README.md'),
        tips_path=os.path.join(ROOT_DIR, 'data', 'tips.json')
    )
    updater.update_readme()
            # Find markers and replace content
            start_idx = content.find(self.start_marker)
            end_idx = content.find(self.end_marker) + len(self.end_marker)

            new_content = content[:start_idx] + status_section + content[end_idx:]

            if new_content == content:
                logger.info("No changes detected in README.md content.")
                return False

            with open(self.readme_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            logger.info(f"README successfully updated at {current_time}")
            logger.info(f"Selected Tip: {tip}")
            return True

        except Exception as e:
            logger.error(f"Error updating README: {e}")
            return False

if __name__ == "__main__":
    # Define file paths relative to this script

def get_daily_tip(tips_path):
    """Fetches a daily tip from the tips.json file based on the day of the year."""
    fallback_tip = "Stay curious and keep coding!"
    try:
        if not os.path.exists(tips_path):
            print(f"Error: Tips file not found at {tips_path}")
            return fallback_tip

        with open(tips_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        tips = data.get('tips', [])
        if not tips:
            return fallback_tip

        # Use UTC day of the year to select a tip consistently
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        day_of_year = now_utc.timetuple().tm_yday

        # Consistent selection of tip
        return tips[day_of_year % len(tips)]
    except Exception as e:
        print(f"Error fetching tip: {e}")
        return fallback_tip

def update_readme(readme_path, tips_path):
    """Updates the README.md file with the current UTC timestamp and a daily tip."""
    tip = get_daily_tip(tips_path)
    current_time = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

    try:
        if not os.path.exists(readme_path):
            print(f"Error: README.md not found at {readme_path}")
            return

        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()

        start_marker = '<!-- SYSTEM_STATUS_START -->'
        end_marker = '<!-- SYSTEM_STATUS_END -->'

        if start_marker not in content or end_marker not in content:
            print(f"Error: Markers {start_marker} or {end_marker} not found in README.md")
            return

        # Prepare the status section content
        status_lines = [
            start_marker,
            f"| 🛰️ Status | 🟢 Operational |",
            f"| :--- | :--- |",
            f"| **Last Synchronized** | `{current_time}` |",
            f"| **Tactical Tip** | `{tip}` |",
            end_marker
        ]
        status_section = "\n".join(status_lines)

        # Replace the content between markers
        start_idx = content.find(start_marker)
        end_idx = content.find(end_marker) + len(end_marker)

        new_content = content[:start_idx] + status_section + content[end_idx:]

        # Avoid redundant writes if nothing changed (though timestamp usually changes)
        if new_content == content:
            print("No changes detected in README.md.")
            return

        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"Successfully updated README.md at {current_time}")
        print(f"Tip of the day: {tip}")

    except Exception as e:
        print(f"Failed to update README: {e}")

if __name__ == "__main__":
    # Resolve paths relative to this script's location
    main
    base_dir = os.path.dirname(os.path.abspath(__file__))
    readme_file = os.path.join(base_dir, 'README.md')
    tips_file = os.path.join(base_dir, 'data', 'tips.json')

    manager = ProfileStatusManager(readme_file, tips_file)
    manager.update_readme()
