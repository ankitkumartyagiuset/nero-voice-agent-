"""
Unit tests for Reminders repository and skill.
"""
import pytest
from datetime import datetime, timedelta
from storage.repositories import ReminderRepository
from skills.reminders import RemindersSkill


@pytest.mark.asyncio
async def test_reminders_crud(test_db):
    repo = ReminderRepository(test_db)
    sched = datetime.now() + timedelta(minutes=5)
    model = repo.create("Study Python", sched)

    assert model.id is not None
    assert model.message == "Study Python"

    active = repo.get_all_active()
    assert len(active) == 1
    assert active[0].message == "Study Python"

    # Mark completed
    repo.mark_completed(model.id)
    assert len(repo.get_all_active()) == 0


@pytest.mark.asyncio
async def test_reminders_skill(test_db):
    repo = ReminderRepository(test_db)
    skill = RemindersSkill(repo)

    res = await skill.execute("create_reminder", {"message": "Review pull request", "minutes_ahead": 15})
    assert res.success
    assert "Review pull request" in res.output_message

    list_res = await skill.execute("list_reminders", {})
    assert list_res.success
    assert "Review pull request" in list_res.output_message
