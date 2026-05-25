import json
import datetime
import os

def get_daily_tip():
    """Fetches a daily tip from the data/tips.json file."""
    try:
        with open('data/tips.json', 'r') as f:
            data = json.load(f)
        tips = data['tips']
        # Use day of the year in UTC to select a tip consistently
        day_of_year = datetime.datetime.now(datetime.timezone.utc).timetuple().tm_yday
        return tips[day_of_year % len(tips)]
    except Exception as e:
        print(f"Error fetching tip: {e}")
        return "Stay curious and keep coding!"

def update_readme():
    """Updates the README.md file with the latest status and tip."""
    tip = get_daily_tip()
    # Use timezone-aware datetime for UTC
    current_time = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

    try:
        with open('README.md', 'r') as f:
            content = f.read()

        start_marker = '<!-- SYSTEM_STATUS_START -->'
        end_marker = '<!-- SYSTEM_STATUS_END -->'

        if start_marker not in content or end_marker not in content:
            print("Markers not found in README.md")
            return

        status_section = (
            f"{start_marker}\n"
            f"| 🛰️ Status | 🟢 Operational |\n"
            f"| :--- | :--- |\n"
            f"| **Last Synchronized** | `{current_time}` |\n"
            f"| **Tactical Tip** | `{tip}` |\n"
            f"{end_marker}"
        )

        # Find markers and replace content
        start_idx = content.find(start_marker)
        end_idx = content.find(end_marker) + len(end_marker)

        new_content = content[:start_idx] + status_section + content[end_idx:]

        with open('README.md', 'w') as f:
            f.write(new_content)

        print(f"README successfully updated at {current_time}")
        print(f"Selected Tip: {tip}")

    except Exception as e:
        print(f"Error updating README: {e}")

if __name__ == "__main__":
    update_readme()
