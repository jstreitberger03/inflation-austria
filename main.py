#!/usr/bin/env python3
"""Main entrypoint for generating Austria's inflation figure set."""

import sys

from inflation_report.pipeline import run_report


def main() -> int:
    """Run the report pipeline using the default configuration."""
    return run_report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as exc:
        print(f"\nError: {exc}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
