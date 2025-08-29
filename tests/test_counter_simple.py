"""Simplified counter tests for debugging."""

import pytest
from nicegui.testing import User
from nicegui import ui
from app.database import reset_db


@pytest.fixture()
def new_db():
    """Fresh database for each test."""
    reset_db()
    yield
    reset_db()


async def test_counter_page_basic_load(user: User, new_db) -> None:
    """Basic test that counter page loads."""
    await user.open("/counter")

    # Should see the title
    await user.should_see("Counter Application")

    # Should see initial counter value
    await user.should_see("0")


async def test_counter_buttons_exist(user: User, new_db) -> None:
    """Test that counter buttons are present."""
    await user.open("/counter")

    # Wait for page to load
    await user.should_see("Counter Application")

    # Check that buttons exist
    buttons = list(user.find(ui.button).elements)
    button_texts = [btn.text for btn in buttons]

    assert "+" in button_texts
    assert "-" in button_texts
    assert "Reset" in button_texts


async def test_single_increment(user: User, new_db) -> None:
    """Test single increment operation."""
    await user.open("/counter")

    # Wait for initial load
    await user.should_see("Counter Application")
    await user.should_see("0")

    # Click increment once
    user.find("+").click()

    # Wait for change - check for the specific number
    await user.should_see("1")


async def test_single_decrement(user: User, new_db) -> None:
    """Test single decrement operation."""
    await user.open("/counter")

    # Wait for initial load
    await user.should_see("Counter Application")
    await user.should_see("0")

    # Click decrement once (should go to -1)
    user.find("-").click()

    # Wait for change
    await user.should_see("-1")
