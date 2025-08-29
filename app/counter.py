from nicegui import ui
from sqlmodel import Session, select
from app.database import ENGINE as engine
from app.models import Counter
import logging

logger = logging.getLogger(__name__)


def get_counter(session: Session, name: str = "default") -> Counter:
    """Get counter by name, create if doesn't exist."""
    statement = select(Counter).where(Counter.name == name)
    counter = session.exec(statement).first()

    if counter is None:
        counter = Counter(name=name, value=0)
        session.add(counter)
        session.commit()
        session.refresh(counter)

    return counter


def increment_counter(session: Session, name: str = "default") -> int:
    """Increment counter value and return new value."""
    counter = get_counter(session, name)
    counter.value += 1
    session.add(counter)
    session.commit()
    return counter.value


def decrement_counter(session: Session, name: str = "default") -> int:
    """Decrement counter value and return new value."""
    counter = get_counter(session, name)
    counter.value -= 1
    session.add(counter)
    session.commit()
    return counter.value


def reset_counter(session: Session, name: str = "default") -> int:
    """Reset counter value to 0 and return new value."""
    counter = get_counter(session, name)
    counter.value = 0
    session.add(counter)
    session.commit()
    return counter.value


def create():
    """Create counter application UI."""

    @ui.page("/counter")
    def counter_page():
        # Apply modern theme colors
        ui.colors(
            primary="#2563eb",
            secondary="#64748b",
            accent="#10b981",
            positive="#10b981",
            negative="#ef4444",
            warning="#f59e0b",
            info="#3b82f6",
        )

        # Main container with modern styling
        with ui.column().classes(
            "items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8"
        ):
            # Title
            ui.label("Counter Application").classes("text-4xl font-bold text-gray-800 mb-8")

            # Counter display card
            with ui.card().classes("p-8 bg-white shadow-xl rounded-2xl hover:shadow-2xl transition-shadow min-w-80"):
                # Counter value display
                count_label = (
                    ui.label("0")
                    .classes("text-6xl font-bold text-center text-primary mb-8")
                    .style("font-family: monospace")
                )

                # Button row
                # Event handlers
                def handle_increment():
                    try:
                        with Session(engine) as session:
                            new_value = increment_counter(session)
                            count_label.set_text(str(new_value))
                            ui.notify("Counter incremented!", type="positive", timeout=1000)
                    except Exception as e:
                        logger.error(f"Error incrementing counter: {str(e)}")
                        ui.notify(f"Error incrementing counter: {str(e)}", type="negative")

                def handle_decrement():
                    try:
                        with Session(engine) as session:
                            new_value = decrement_counter(session)
                            count_label.set_text(str(new_value))
                            ui.notify("Counter decremented!", type="info", timeout=1000)
                    except Exception as e:
                        logger.error(f"Error decrementing counter: {str(e)}")
                        ui.notify(f"Error decrementing counter: {str(e)}", type="negative")

                def handle_reset():
                    try:
                        with Session(engine) as session:
                            new_value = reset_counter(session)
                            count_label.set_text(str(new_value))
                            ui.notify("Counter reset to 0!", type="warning", timeout=1000)
                    except Exception as e:
                        logger.error(f"Error resetting counter: {str(e)}")
                        ui.notify(f"Error resetting counter: {str(e)}", type="negative")

                with ui.row().classes("gap-4 justify-center w-full"):
                    # Decrement button
                    ui.button("-", on_click=handle_decrement).classes(
                        "w-16 h-16 text-2xl font-bold bg-red-500 hover:bg-red-600 text-white rounded-full shadow-lg hover:shadow-xl transition-all"
                    )

                    # Reset button
                    ui.button("Reset", on_click=handle_reset).classes(
                        "px-6 py-3 font-semibold bg-gray-500 hover:bg-gray-600 text-white rounded-lg shadow-lg hover:shadow-xl transition-all"
                    )

                    # Increment button
                    ui.button("+", on_click=handle_increment).classes(
                        "w-16 h-16 text-2xl font-bold bg-green-500 hover:bg-green-600 text-white rounded-full shadow-lg hover:shadow-xl transition-all"
                    )

                # Current counter info
                ui.label("Counter: default").classes("text-sm text-gray-500 text-center mt-4")

        # Initialize counter value on page load
        def load_counter():
            with Session(engine) as session:
                counter = get_counter(session)
                count_label.set_text(str(counter.value))

        load_counter()

    # Add counter link to the main navigation
    @ui.page("/")
    def index():
        with ui.column().classes(
            "items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8"
        ):
            ui.label("Welcome to Counter App").classes("text-4xl font-bold text-gray-800 mb-8")

            with ui.card().classes("p-6 bg-white shadow-xl rounded-xl"):
                ui.label("Click below to access the counter application").classes(
                    "text-lg text-gray-600 mb-4 text-center"
                )
                ui.link("Open Counter", "/counter").classes(
                    "bg-primary text-white px-6 py-3 rounded-lg font-semibold hover:bg-primary-dark transition-colors no-underline"
                )
