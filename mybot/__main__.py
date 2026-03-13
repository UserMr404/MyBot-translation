"""Entry point for `python -m mybot`."""

import sys

from mybot.app import App, parse_args


def main() -> None:
    """Launch MyBot application."""
    args = parse_args()
    app = App(args)
    sys.exit(app.run())


if __name__ == "__main__":
    main()
