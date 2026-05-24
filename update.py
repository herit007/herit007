import json
import datetime
import os

def get_daily_tip():
    with open('data/tips.json', 'r') as f:
        data = json.load(f)
    tips = data['tips']
    # Use day of the year to select a tip
    day_of_year = datetime.datetime.now().timetuple().tm_yday
    return tips[day_of_year % len(tips)]

def update_readme():
    tip = get_daily_tip()
    # Use timezone-aware datetime for UTC
    current_time = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

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

    new_content = content[:content.find(start_marker)] + status_section + content[content.find(end_marker) + len(end_marker):]

    with open('README.md', 'w') as f:
        f.write(new_content)

    print(f"README updated with tip: {tip}")

if __name__ == "__main__":
    update_readme()
