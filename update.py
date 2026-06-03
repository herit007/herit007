import json
import datetime
import os

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
    base_dir = os.path.dirname(os.path.abspath(__file__))
    readme_file = os.path.join(base_dir, 'README.md')
    tips_file = os.path.join(base_dir, 'data', 'tips.json')

    update_readme(readme_file, tips_file)
