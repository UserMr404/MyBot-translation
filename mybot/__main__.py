"""Entry point for `python -m mybot`."""

import sys


def main() -> None:
    """Launch MyBot application."""
    # Phase 6 will implement full App class with GUI
    print(f"MyBot v{__import__('mybot').__version__} - not yet fully implemented")
    print("Phase 1 foundation modules are available for import.")
    sys.exit(0)


if __name__ == "__main__":
    main()
