"""Enumerations.py: NeoPixel Indicator Module."""

from enum import Enum, auto, unique
from typing import Tuple

ColorType = Tuple[int, int, int]


class Color:
    """This is a doctring."""

    # Color.BLACK is used in npin module code, and should not be modified.
    BLACK = (0, 0, 0)

    # WHITE, RED, GREEN and BLUE should probably be left alone for the sake of clarity.
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

    # Everything else is up for grabs - add and customize to your heart's content!
    ORANGE = (255, 128, 0)
    CYAN = (0, 128, 255)


@unique
class Value(Enum):
    """Make this a docstring."""

    CURRENT = auto()
    TARGET = auto()


class Script:
    """Make this a docstring."""

    @unique
    class Type(Enum):
        """Make this a docstring."""

        ONCE = auto()
        LOOP = auto()

    @unique
    class Command(Enum):
        """Make this a docstring."""

        COLOR = auto()
        BRIGHTNESS = auto()
        WAIT = auto()

    @unique
    class Run(Enum):
        """Make this a docstring."""

        NOW = auto()
        AFTER = auto()
