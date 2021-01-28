"""Mode.py: NeoPixel Indicator Module."""

from typing import Iterator

from npin.Constants import Script
from npin.Counter import SharedCounter

DEFAULT_MODES = {
    "active": {
        "type": Script.Type.ONCE,
        "sync": False,
        "script": [
            (Script.Command.BRIGHTNESS, 100, 1.0),
        ],
    },
    "idle": {
        "type": Script.Type.ONCE,
        "sync": False,
        "script": [
            (Script.Command.BRIGHTNESS, 100, 0.2),
        ],
    },
    "off": {
        "type": Script.Type.ONCE,
        "sync": False,
        "script": [
            (Script.Command.BRIGHTNESS, 100, 0.0),
        ],
    },
    "blink": {
        "type": Script.Type.LOOP,
        "sync": True,
        "script": [
            (Script.Command.BRIGHTNESS, 50, 0.6),
            (Script.Command.WAIT, 25),
            (Script.Command.BRIGHTNESS, 50, 0.2),
        ],
    },
}


class Mode:
    """This is a docstring."""

    def __init__(self, modes: dict = DEFAULT_MODES) -> None:
        """Make this a docstring."""
        self._modes = dict()
        for m in modes:
            self.add(m, modes[m])

    def __iter__(self) -> Iterator[dict]:
        """Make this a docstring."""
        for m in self._modes:
            yield self._modes[m]

    def __contains__(self, value: str) -> bool:
        """Make this a docstring."""
        return value in self._modes

    def __getitem__(self, value: str) -> dict:
        """Make this a docstring."""
        return self._modes[value]

    def __len__(self) -> int:
        """Make this a docstring."""
        return len(self._modes)

    def add(self, name: str, data: dict) -> None:
        """Make this a docstring."""
        # validate mode name
        if name not in self._modes:
            self._modes[name] = dict()
        else:
            raise KeyError("A mode with the specified name already exists")

        # validate script type
        if "type" in data:
            if isinstance(data["type"], Script.Type):
                self._modes[name]["type"] = data["type"]
            else:
                raise ValueError("Incorrect Script.Type specified")
        else:
            self._modes[name]["type"] = Script.Type.ONCE

        # validate script sync
        if "sync" in data:
            if isinstance(data["sync"], bool):
                self._modes[name]["sync"] = data["sync"]
            else:
                raise ValueError("Sync property must be either True or False")
        else:
            self._modes[name]["sync"] = False

        # process mode script and determine script period
        period = 0
        processed_script = []
        for s in data["script"]:
            cycle = period
            if isinstance(s[0], Script.Command):
                period += s[1]
            processed_script.append((cycle,) + s)
        self._modes[name]["script"] = processed_script
        self._modes[name]["period"] = period
        if self._modes[name]["sync"] is True:
            SharedCounter.add(name, period)

    def remove(self, name: str) -> None:
        """Make this a docstring."""
        del self._modes[name]
