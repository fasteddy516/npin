"""Element.py: NeoPixel Indicator Module."""

from typing import Iterator, Tuple

from npin.Constants import Color, ColorType, Script, Value
from npin.Counter import SharedCounter
from npin.Mode import Mode


class Element:
    """This is a doctring."""

    modes = Mode()

    def __init__(
        self,
        name: str = "Element",
        size: int = 1,
        offset: int = None,
        color: ColorType = Color.BLACK,
        brightness: float = 0.0,
    ) -> None:
        """Make this is a doctring."""
        self._name = name
        self._size = size
        self._offset = offset

        self._color_target = color
        self._color_now = Color.BLACK
        self._color_int = Color.BLACK
        self._color_cycles = 1
        self._color_step = (0.0, 0.0, 0.0)

        self._brightness_target = brightness
        self._brightness_now = 0.0
        self._brightness_cycles = 1
        self._brightness_step = 0.0

        self._script = []
        self._script_cycle = 0
        self._script_period = 0
        self._script_type = Script.Type.ONCE
        self._next_script = None

        self._current = Color.BLACK

    def __str__(self) -> str:
        """Make this is a docstring."""
        return (
            f"[{self.offset:03d}:{self.offset + self._size-1:03d}] "
            + f"({self._color_target[0]:03d}, {self._color_target[1]:03d}, {self._color_target[2]:03d}) < "
            + f"({self._current[0]:03d}, {self._current[1]:03d}, {self._current[2]:03d}) "
            + f"| {self._name:50}\n"
        )

    def __len__(self) -> int:
        """Make this a docstring."""
        return self._size

    def __iter__(self) -> Iterator[Tuple[int, ColorType]]:
        """Make this a docstring."""
        for i in range(self._size):
            yield self._offset + i, self._color_int

    @property
    def offset(self) -> int:
        """Make this a docstring."""
        if self._offset is None:
            return -1
        else:
            return self._offset

    @offset.setter
    def offset(self, value: int) -> None:
        """Make this a docstring."""
        if self._offset is None:
            self._offset = value
        else:
            raise ValueError("Element offsets can not be modified after they are set.")

    @property
    def name(self) -> str:
        """Make this a docstring."""
        return self._name

    @property
    def is_changing(self) -> bool:
        """Make this a docstring."""
        if self._color_cycles or self._brightness_cycles:
            return True
        else:
            return False

    def get_color(self, value: Value = Value.CURRENT) -> ColorType:
        """Make this a docstring."""
        return self._color_int if value == Value.CURRENT else self._color_target

    def set_color(self, color: ColorType, cycles: int = 1) -> None:
        """Make this a docstring."""
        cycles = max(cycles, 1)
        self._color_target = color
        self._color_step = tuple(
            (self._color_target[i] - self._color_now[i]) / cycles
            for i in range(len(self._color_now))
        )
        self._color_cycles = cycles

    def get_brightness(self, value: Value = Value.CURRENT) -> float:
        """Make this a docstring."""
        return (
            self._brightness_now if value == Value.CURRENT else self._brightness_target
        )

    def set_brightness(self, brightness: float, cycles: int = 1) -> None:
        """Make this a docstring."""
        cycles = max(cycles, 1)
        b = float(brightness)
        if b >= 0.0 and b <= 1.0:
            self._brightness_target = b
            self._brightness_step = (
                self._brightness_target - self._brightness_now
            ) / cycles
            self._brightness_cycles = cycles
        else:
            raise ValueError("Brightness range is from 0.0 to 1.0.")

    def _load_script(self, mode: str) -> None:
        """Make this a docstring."""
        if mode in Element.modes:
            self._script = list(Element.modes[mode]["script"])
            self._script_type = Element.modes[mode]["type"]
            self._script_period = Element.modes[mode]["period"]
            if Element.modes[mode]["sync"] is True:
                self._script_cycle = SharedCounter.counters[mode].count
            else:
                self._script_cycle = 0
            self._next_script = None
        else:
            raise KeyError("The specified mode does not exist")

    def set_mode(self, mode: str, when: Script.Run = Script.Run.NOW) -> None:
        """Make this a docstring."""
        if mode in Element.modes:
            if when == Script.Run.NOW or not self._script:
                self._load_script(mode)
            elif when == Script.Run.AFTER:
                self._next_script = mode
        else:
            raise KeyError("The specified mode does not exist")

    def update(self, master_cycle: int = 0) -> bool:
        """Make this is a docstring."""
        changed = False

        if self._color_cycles:
            changed = True
            self._color_cycles -= 1
            if self._color_cycles == 0:
                self._color_now = self._color_target
            else:
                self._color_now = tuple(
                    self._color_now[i] + self._color_step[i]
                    for i in range(len(self._color_now))
                )

        if self._brightness_cycles:
            changed = True
            self._brightness_cycles -= 1
            if self._brightness_cycles == 0:
                self._brightness_now = self._brightness_target
            else:
                self._brightness_now += self._brightness_step

        if changed:
            self._color_int = tuple(
                [int(i * self._brightness_now) for i in self._color_now]
            )

        if self._script:
            for s in self._script:
                if s[0] == self._script_cycle:
                    if s[1] == Script.Command.COLOR:
                        self.set_color(s[3], cycles=s[2])
                    elif s[1] == Script.Command.BRIGHTNESS:
                        self.set_brightness(s[3], cycles=s[2])
                    break

            self._script_cycle += 1
            if self._script_cycle >= self._script_period:
                if self._script_type == Script.Type.LOOP:
                    self._script_cycle = 0
                else:
                    self._script.clear()
                if self._next_script:
                    self._load_script(self._next_script)

        if self._color_int != self._current:
            self._current = self._color_int
            return True
        else:
            return False
