"""Group.py: NeoPixel Indicator Module."""

import threading
import time
from typing import Any, List, overload

import neopixel

from npin.Constants import Color
from npin.Counter import SharedCounter
from npin.Element import Element


class Group:
    """Make this a docstring."""

    def __init__(
        self, elements: List[Element] = [], brightness: float = 1.0, pin: Any = None
    ) -> None:
        """Make this is a docstring."""
        self._brightness = 0
        self._brightness_target = 0
        self._brightness_cycles = 0
        self.set_brightness(brightness)
        self._brightness = self._brightness_target
        self._started = False
        self._pixels = None
        self._thread = None
        self._pin = pin
        self._element_dict = dict()
        self._elements = []
        if not isinstance(elements, list):
            raise TypeError("'_elements' must be of type list[Element].")
        else:
            for e in elements:
                self.add_element(e)

    def __enter__(self):
        """Make this a docstring."""
        self.loop_start()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """Make this a docstring."""
        if self._thread is not None:
            self.loop_stop()
        self._pixels.deinit()

    def __str__(self) -> str:
        """Make this is a docstring."""
        s = " ADDRESS   TARGET COLOR      CURRENT COLOR    NAME\n"
        for e in self._elements:
            s += str(e)
        return s

    def __len__(self) -> int:
        """Make this is a docstring."""
        return len(self._elements)

    @overload
    def __getitem__(self, item: int) -> Element:
        """Make this a docstring."""
        ...

    @overload
    def __getitem__(self, item: str) -> Element:
        """Make this a docstring."""
        ...

    def __getitem__(self, item) -> Element:
        """Make this a docstring."""
        if isinstance(item, int):
            return self._elements[item]
        elif isinstance(item, str):
            if item in self._element_dict:
                return self._elements[self._element_dict[item]]
            else:
                raise KeyError("Requested element does not exist.")
        else:
            raise TypeError("Elements are accessed by index (int) or name (str).")

    def __iter__(self):
        """Make this a docstring."""
        for i in range(len(self)):
            yield self._elements[i]

    @property
    def pixel_count(self) -> int:
        """Make this a docstring."""
        length = 0
        for e in self._elements:
            length += len(e)
        return length

    @property
    def is_started(self) -> bool:
        """Make this a docstring."""
        return self._started

    @property
    def brightness(self) -> float:
        """Make this a docstring."""
        return self._brightness

    @property
    def is_changing(self) -> bool:
        """Make this a docstring."""
        for e in self._elements:
            if e.is_changing:
                return True
        return False

    def set_brightness(self, value: float, cycles: int = 1) -> None:
        """Make this a docstring."""
        b = float(value)
        if b >= 0.0 and b <= 1.0:
            self._brightness_target = b
            self._brightness_step = (
                self._brightness_target - self._brightness
            ) / cycles
            self._brightness_cycles = cycles
        else:
            raise ValueError("Brightness range is from 0.0 to 1.0.")

    def add_element(self, element: Element) -> None:
        """Make this is a docstring."""
        if not isinstance(element, Element):
            raise TypeError
        if self._started:
            raise RuntimeError("Elements cannot be added after start().")
        offset = self.pixel_count
        self._elements.append(element)
        self._elements[-1].offset = offset
        if len(element.name) and element.name not in self._element_dict:
            self._element_dict[element.name] = len(self) - 1

    def start(self, pin: Any = None, pixel_order: str = None) -> None:
        """Make this is a docstring."""
        if not len(self):
            raise ValueError("Cannot start a group before adding _elements.")
        if self._started or self._pixels is not None:
            raise RuntimeError("Group has already been started.")
        if pin is None:
            pin = self._pin
        self._pixels = neopixel.NeoPixel(
            pin,
            self.pixel_count,
            brightness=self.brightness,
            auto_write=False,
            pixel_order=pixel_order,
        )
        self._pixels.fill(Color.BLACK)
        self._pixels.show()
        self._started = True

    def loop_start(self, pin: Any = None, pixel_order: str = None) -> None:
        """Make this a docstring."""
        if self._thread is not None:
            raise RuntimeError("Loop is already running.")
        if not self._started and self._pixels is None:
            self.start(pin, pixel_order)
        self._thread = _GroupThread(self)
        self._thread.start()

    def loop_stop(self, timeout: int = 5) -> None:
        """Make this a docstring."""
        if not isinstance(self._thread, _GroupThread):
            raise RuntimeError("Loop thread does not exist.")
        if not self._thread.is_alive():
            raise RuntimeError("Loop is already stopped.")
        self._thread.join(timeout=timeout)

    def update(self) -> bool:
        """Make this a docstring."""
        if not self._started:
            raise RuntimeError("Group has not been started.")
        changed = False

        for element in self._elements:
            if element.update():
                for offset, color in element:
                    self._pixels[offset] = color
                changed = True

        if self._brightness_cycles:
            self._brightness_cycles -= 1
            if self._brightness_cycles == 0:
                self._brightness = self._brightness_target
            else:
                self._brightness += self._brightness_step
            changed = True
            self._pixels.brightness = self._brightness

        SharedCounter.update_all()

        return changed


class _GroupThread(threading.Thread):
    """Make this a docstring."""

    def __init__(self, group: Group) -> None:
        """Make this a docstring."""
        self._stop_event = threading.Event()
        self._group = group
        threading.Thread.__init__(self, name="Loop")

    def run(self) -> None:
        """Make this a docstring."""
        cycles = 0
        cycleTotal = 0.0
        cycleProcess = 0.0
        cycleWrite = 0.0
        idle_count = 0

        target_time = 0.0099

        while not self._stop_event.is_set():
            # record start time of cycle
            cycleStart = time.perf_counter()
            changed = self._group.update()
            processingComplete = time.perf_counter()
            if changed:
                self._group._pixels.show()
            else:
                idle_count += 1
            cycle_time = time.perf_counter() - cycleStart
            if cycle_time < target_time:
                time.sleep(target_time - cycle_time)

            # process cycle time measurement
            cycleFinish = time.perf_counter()
            cycleTotal += cycleFinish - cycleStart
            cycleProcess += processingComplete - cycleStart
            cycleWrite += cycleFinish - processingComplete
            cycles += 1
            if cycles >= 100:
                print(
                    f"Cycle Time = {cycleFinish - cycleStart:06.4f}s ({processingComplete - cycleStart:06.4f}/{cycleFinish - processingComplete:06.4f}),",
                    f"Average = {cycleTotal / cycles:06.4f} ({cycleProcess / cycles:06.4f}/{cycleWrite / cycles:06.4f}),",
                    f"Work/Idle = {cycles - idle_count:03d}/{idle_count:03d},",
                    f"Cycles = {cycles}",
                )
                cycles = 0
                cycleTotal = 0.0
                cycleProcess = 0.0
                cycleWrite = 0.0
                idle_count = 0

        for e in self._group._elements:
            e.set_color(Color.BLACK, cycles=50)

        while self._group.update():
            self._group._pixels.show()

    def join(self, timeout: float = None) -> None:
        """Make this a docstring."""
        self._stop_event.set()
        threading.Thread.join(self, timeout)
