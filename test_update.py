import os
import tempfile
import json
import pytest
from update import ProfileStatusManager

def test_get_daily_tip_fallback():
    # If file doesn't exist, should return default tip
    manager = ProfileStatusManager("nonexistent_readme.md", "nonexistent_tips.json")
    assert manager.get_daily_tip() == ProfileStatusManager.DEFAULT_TIP

def test_get_daily_tip_valid():
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as f:
        json.dump({"tips": ["Tip A", "Tip B", "Tip C"]}, f)
        tips_path = f.name

    try:
        manager = ProfileStatusManager("nonexistent_readme.md", tips_path)
        tip = manager.get_daily_tip()
        assert tip in ["Tip A", "Tip B", "Tip C"]
    finally:
        os.remove(tips_path)

def test_update_readme():
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.md', delete=False) as readme_file:
        readme_file.write(
            "Some header\n"
            "<!-- SYSTEM_STATUS_START -->\n"
            "Old stuff\n"
            "<!-- SYSTEM_STATUS_END -->\n"
            "Some footer"
        )
        readme_path = readme_file.name

    with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as tips_file:
        json.dump({"tips": ["A test tip"]}, fp=tips_file)
        tips_path = tips_file.name

    try:
        manager = ProfileStatusManager(readme_path, tips_path)
        updated = manager.update_readme()
        assert updated is True

        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert "A test tip" in content
        assert "🟢 Operational" in content
        assert "<!-- SYSTEM_STATUS_START -->" in content
        assert "<!-- SYSTEM_STATUS_END -->" in content

        # Check redundant update
        assert manager.update_readme() is False
    finally:
        os.remove(readme_path)
        os.remove(tips_path)
