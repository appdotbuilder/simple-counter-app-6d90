"""Tests for counter service logic."""

import pytest
from sqlmodel import Session
from app.database import ENGINE as engine, reset_db
from app.counter import get_counter, increment_counter, decrement_counter, reset_counter
from app.models import Counter


@pytest.fixture()
def new_db():
    """Fresh database for each test."""
    reset_db()
    yield
    reset_db()


def test_get_counter_creates_if_not_exists(new_db):
    """Test that get_counter creates a new counter if it doesn't exist."""
    with Session(engine) as session:
        counter = get_counter(session, "test_counter")

        assert counter is not None
        assert counter.name == "test_counter"
        assert counter.value == 0
        assert counter.id is not None


def test_get_counter_returns_existing(new_db):
    """Test that get_counter returns existing counter."""
    with Session(engine) as session:
        # Create a counter with a specific value
        existing_counter = Counter(name="existing", value=42)
        session.add(existing_counter)
        session.commit()
        session.refresh(existing_counter)

        # Retrieve the same counter
        retrieved_counter = get_counter(session, "existing")

        assert retrieved_counter.id == existing_counter.id
        assert retrieved_counter.name == "existing"
        assert retrieved_counter.value == 42


def test_increment_counter_default(new_db):
    """Test incrementing the default counter."""
    with Session(engine) as session:
        # First increment should create counter at 1
        value = increment_counter(session)
        assert value == 1

        # Second increment should go to 2
        value = increment_counter(session)
        assert value == 2

        # Verify in database
        counter = get_counter(session)
        assert counter.value == 2


def test_increment_counter_named(new_db):
    """Test incrementing a named counter."""
    with Session(engine) as session:
        value = increment_counter(session, "named_counter")
        assert value == 1

        # Verify it's separate from default
        default_value = increment_counter(session, "default")
        assert default_value == 1

        # Named counter should still be at 1
        named_counter = get_counter(session, "named_counter")
        assert named_counter.value == 1


def test_decrement_counter_default(new_db):
    """Test decrementing the default counter."""
    with Session(engine) as session:
        # Start with some increments
        increment_counter(session)
        increment_counter(session)
        increment_counter(session)  # Now at 3

        # Decrement
        value = decrement_counter(session)
        assert value == 2

        value = decrement_counter(session)
        assert value == 1


def test_decrement_counter_negative(new_db):
    """Test decrementing counter can go negative."""
    with Session(engine) as session:
        # Decrement from initial 0
        value = decrement_counter(session)
        assert value == -1

        value = decrement_counter(session)
        assert value == -2


def test_decrement_counter_named(new_db):
    """Test decrementing a named counter."""
    with Session(engine) as session:
        # Set up named counter
        increment_counter(session, "test_counter")
        increment_counter(session, "test_counter")  # At 2

        value = decrement_counter(session, "test_counter")
        assert value == 1


def test_reset_counter_default(new_db):
    """Test resetting the default counter."""
    with Session(engine) as session:
        # Set counter to some value
        increment_counter(session)
        increment_counter(session)
        increment_counter(session)  # At 3

        # Reset
        value = reset_counter(session)
        assert value == 0

        # Verify in database
        counter = get_counter(session)
        assert counter.value == 0


def test_reset_counter_negative(new_db):
    """Test resetting counter that was negative."""
    with Session(engine) as session:
        # Make counter negative
        decrement_counter(session)
        decrement_counter(session)  # At -2

        # Reset
        value = reset_counter(session)
        assert value == 0


def test_reset_counter_named(new_db):
    """Test resetting a named counter."""
    with Session(engine) as session:
        # Set up named counter
        increment_counter(session, "reset_test")
        increment_counter(session, "reset_test")  # At 2

        # Reset
        value = reset_counter(session, "reset_test")
        assert value == 0

        # Verify default counter is unaffected
        default_counter = get_counter(session, "default")
        assert default_counter.value == 0  # Should still be initial value


def test_multiple_counters_independent(new_db):
    """Test that multiple counters operate independently."""
    with Session(engine) as session:
        # Increment different counters
        val1 = increment_counter(session, "counter1")
        val2 = increment_counter(session, "counter2")
        val1_again = increment_counter(session, "counter1")

        assert val1 == 1
        assert val2 == 1
        assert val1_again == 2

        # Verify final states
        counter1 = get_counter(session, "counter1")
        counter2 = get_counter(session, "counter2")

        assert counter1.value == 2
        assert counter2.value == 1


def test_counter_persistence(new_db):
    """Test that counter values persist across sessions."""
    # First session - create and increment
    with Session(engine) as session:
        increment_counter(session, "persistent")
        increment_counter(session, "persistent")
        increment_counter(session, "persistent")

    # Second session - verify value persisted
    with Session(engine) as session:
        counter = get_counter(session, "persistent")
        assert counter.value == 3

        # Modify in second session
        value = increment_counter(session, "persistent")
        assert value == 4

    # Third session - verify again
    with Session(engine) as session:
        counter = get_counter(session, "persistent")
        assert counter.value == 4


def test_edge_cases(new_db):
    """Test edge cases and boundary conditions."""
    with Session(engine) as session:
        # Very large positive numbers
        counter = Counter(name="large", value=999999)
        session.add(counter)
        session.commit()

        value = increment_counter(session, "large")
        assert value == 1000000

        # Very large negative numbers
        counter2 = Counter(name="negative", value=-999999)
        session.add(counter2)
        session.commit()

        value = decrement_counter(session, "negative")
        assert value == -1000000


def test_counter_names_case_sensitive(new_db):
    """Test that counter names are case sensitive."""
    with Session(engine) as session:
        increment_counter(session, "Test")
        increment_counter(session, "test")
        increment_counter(session, "TEST")

        counter_test = get_counter(session, "Test")
        counter_test_lower = get_counter(session, "test")
        counter_test_upper = get_counter(session, "TEST")

        assert counter_test.value == 1
        assert counter_test_lower.value == 1
        assert counter_test_upper.value == 1
        assert counter_test.id != counter_test_lower.id
        assert counter_test.id != counter_test_upper.id
