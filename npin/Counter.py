"""Counter.py: NeoPixel Indicator Module."""


class Counter:
    """This is a docstring."""

    def __init__(self, count: int) -> None:
        """Make this a docstring."""
        self._count = 1
        self._total = count

    @property
    def count(self) -> int:
        """Make this a docstring."""
        return self._count

    @property
    def total(self) -> int:
        """Make this a docstring."""
        return self._total

    def __str__(self) -> str:
        """Make this a docstring."""
        return f"{self._count}/{self._total}"

    def update(self) -> None:
        """Make this a docstring."""
        if self._count == self._total:
            self._count = 1
        else:
            self._count += 1


class SharedCounter:
    """Make this a docstring."""

    counters = dict()

    @staticmethod
    def add(name: str, count: int) -> None:
        """Make this a docstring."""
        if name not in SharedCounter.counters:
            SharedCounter.counters[name] = Counter(count)
        else:
            raise KeyError(f"Requested counter name {name} already exists.")

    @staticmethod
    def remove(name: str) -> None:
        """Make this a docstring."""
        del SharedCounter.counters[name]

    @staticmethod
    def update_all() -> None:
        """Make this a docstring."""
        for c in SharedCounter.counters:
            SharedCounter.counters[c].update()
