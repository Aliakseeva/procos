"""
Application runner. Usage:
> python3 run.py
"""
import asyncio

from procos.cli import main
from procos.handlers import *  # noqa: F401


def run():
    try:
        asyncio.run(main())
    except EOFError:
        print()


if __name__ == "__main__":
    """Run the program."""
    run()
