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
