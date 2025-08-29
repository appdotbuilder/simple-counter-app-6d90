"""Tests for counter UI functionality."""

import pytest
from nicegui.testing import User
from nicegui import ui
from app.database import reset_db
from sqlmodel import Session
from app.database import ENGINE as engine
from app.models import Counter


@pytest.fixture()
def new_db():
    """Fresh database for each test."""
    reset_db()
    yield
    reset_db()


async def test_counter_page_loads(user: User, new_db) -> None:
    """Test that the counter page loads with initial state."""
    await user.open("/counter")

    # Check title is present
    await user.should_see("Counter Application")

    # Check initial counter value is 0
    await user.should_see("0")

    # Check buttons are present
    increment_buttons = list(user.find(ui.button).elements)
    button_texts = [btn.text for btn in increment_buttons if btn.text in ["+", "-", "Reset"]]

    assert "+" in button_texts
    assert "-" in button_texts
    assert "Reset" in button_texts


async def test_counter_increment_functionality(user: User, new_db) -> None:
    """Test incrementing the counter."""
    await user.open("/counter")

    # Initial state - wait for page to load
    await user.should_see("Counter Application")

    # Click increment button and wait for update
    user.find("+").click()
    await user.should_see("1")

    # Click increment again and wait
    user.find("+").click()
    await user.should_see("2")


async def test_counter_decrement_functionality(user: User, new_db) -> None:
    """Test decrementing the counter."""
    await user.open("/counter")

    # Wait for page load
    await user.should_see("Counter Application")

    # Start from initial 0, decrement should go negative
    user.find("-").click()
    await user.should_see("-1")

    # Decrement again
    user.find("-").click()
    await user.should_see("-2")


async def test_counter_reset_functionality(user: User, new_db) -> None:
    """Test resetting the counter."""
    await user.open("/counter")

    # Increment to some value
    user.find("+").click()
    await user.should_see("1")
    user.find("+").click()
    await user.should_see("2")
    user.find("+").click()
    await user.should_see("3")

    # Reset counter
    user.find("Reset").click()
    await user.should_see("0")

    # Should see reset notification
    await user.should_see("Counter reset to 0!")


async def test_counter_mixed_operations(user: User, new_db) -> None:
    """Test mixed increment/decrement operations."""
    await user.open("/counter")

    # Start at 0, do some operations
    user.find("+").click()
    await user.should_see("1")

    user.find("+").click()
    await user.should_see("2")

    user.find("-").click()
    await user.should_see("1")

    user.find("-").click()
    await user.should_see("0")

    user.find("-").click()
    await user.should_see("-1")


async def test_counter_persistence_across_reloads(user: User, new_db) -> None:
    """Test that counter value persists when page is reloaded."""
    await user.open("/counter")

    # Set counter to some value
    user.find("+").click()
    await user.should_see("1")
    user.find("+").click()
    await user.should_see("2")
    user.find("+").click()
    await user.should_see("3")

    # Reload page
    await user.open("/counter")

    # Value should persist
    await user.should_see("3")


async def test_index_page_navigation(user: User, new_db) -> None:
    """Test navigation from index page to counter."""
    await user.open("/")

    # Check welcome message
    await user.should_see("Welcome to Counter App")

    # Check link is present
    await user.should_see("Open Counter")

    # Click link to navigate to counter
    user.find("Open Counter").click()

    # Should be on counter page
    await user.should_see("Counter Application")
    await user.should_see("0")


async def test_counter_with_existing_data(user: User, new_db) -> None:
    """Test counter page with pre-existing counter data."""
    # Pre-populate database with counter data
    with Session(engine) as session:
        counter = Counter(name="default", value=42)
        session.add(counter)
        session.commit()

    await user.open("/counter")

    # Should show existing value
    await user.should_see("42")

    # Operations should work from existing value
    user.find("+").click()
    await user.should_see("43")

    user.find("-").click()
    await user.should_see("42")

    user.find("Reset").click()
    await user.should_see("0")


async def test_counter_notifications(user: User, new_db) -> None:
    """Test that appropriate notifications are shown."""
    await user.open("/counter")

    # Test increment notification
    user.find("+").click()
    await user.should_see("Counter incremented!")

    # Test decrement notification
    user.find("-").click()
    await user.should_see("Counter decremented!")

    # Test reset notification
    user.find("Reset").click()
    await user.should_see("Counter reset to 0!")


async def test_counter_large_numbers(user: User, new_db) -> None:
    """Test counter with large numbers."""
    # Pre-populate with large number
    with Session(engine) as session:
        counter = Counter(name="default", value=999)
        session.add(counter)
        session.commit()

    await user.open("/counter")

    # Should display large number correctly
    await user.should_see("999")

    # Should increment correctly
    user.find("+").click()
    await user.should_see("1000")


async def test_counter_negative_numbers(user: User, new_db) -> None:
    """Test counter with negative numbers."""
    # Pre-populate with negative number
    with Session(engine) as session:
        counter = Counter(name="default", value=-10)
        session.add(counter)
        session.commit()

    await user.open("/counter")

    # Should display negative number correctly
    await user.should_see("-10")

    # Should increment towards zero
    user.find("+").click()
    await user.should_see("-9")

    # Should decrement away from zero
    user.find("-").click()
    await user.should_see("-10")
