import sys
from pathlib import Path

# Ensure the project root is on the path so `src.*` imports work
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.ui.app import App


def main() -> None:
    """Launch the Smart Download Organizer application."""
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
