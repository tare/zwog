"""Routines for processing workouts."""
import argparse
import sys
from dataclasses import dataclass
from importlib.metadata import version
from typing import Any, List, NoReturn, Optional, Tuple, Union
from xml.etree.ElementTree import Element, ElementTree, SubElement, tostring

from lark import Lark, Transformer

from zwog.constants import (
    INTERVALST_LENGTH,
    SECONDS_IN_HOUR,
    SECONDS_IN_MINUTE,
    ZWOG_GRAMMAR,
)


@dataclass
class Interval:
    """Interval data."""

    duration: int
    power: Union[float, List[float]]


@dataclass
class Block:
    """Block data."""

    intervals: List[Interval]
    repeats: int = 1


class WorkoutTransformer(Transformer[Any, Any]):
    """Class to process workout parse-trees."""

    INT = int
    NUMBER = float
    TIME_UNIT = str
    duration = tuple
    steady_state = tuple
    ramp = tuple
    workout = list

    @staticmethod
    def durations(d: List[Tuple[Union[int, float], str]]) -> int:
        """Return total duration."""

        def duration(x: Union[int, float], y: str) -> int:
            if x <= 0:
                msg = "Duration values need to be strictly positive"
                raise ValueError(msg)
            if y in {"hrs", "h"}:
                return int(x * SECONDS_IN_HOUR)
            if y in {"min", "m"}:
                return int(x * SECONDS_IN_MINUTE)
            if y in {"sec", "s"}:
                return int(x)
            msg = f"Unexpected unit of time: {y}"
            raise ValueError(msg)

        total_duration = sum(duration(*x) for x in d)  # noqa: FURB140

        if not total_duration > 0:
            msg = "Interval duration values need to be strictly positive"
            raise ValueError(msg)

        return total_duration

    @staticmethod
    def interval(s: List[Tuple[int, Union[float, List[float]]]]) -> Interval:
        """Return steady-state."""
        return Interval(duration=s[0][0], power=s[0][1])

    @staticmethod
    def power(p: List[float]) -> Union[float, List[float]]:
        """Return power."""
        if any(x < 0 for x in p):
            msg = "Power values need to be positive"
            raise ValueError(msg)
        if len(p) == 1:
            return p[0]
        return p

    @staticmethod
    def repeats(r: List[int]) -> Tuple[str, int]:
        """Return repeats."""
        if r[0] <= 0:
            msg = "Repeat multipliers need to be strictly positive"
            raise ValueError(msg)
        return "repeats", r[0]

    @staticmethod
    def intervals(i: List[Interval]) -> Tuple[str, List[Interval]]:
        """Return intervals."""
        return "intervals", i

    @staticmethod
    def block(
        b: List[Tuple[str, Union[int, List[Interval]]]],
    ) -> Block:
        """Return block."""
        return Block(**dict(x for x in b if x))  # type: ignore[arg-type]


class ZWOG:
    """Zwift workout generator (ZWOG)."""

    def __init__(
        self,
        workout: str,
        author: str = ("Zwift workout generator (https://github.com/tare/zwog)"),
        name: str = "Structured workout",
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
    ) -> None:
        """Initialize ZWOG.

        Args:
            workout: Workout as a string.
            author: Author.
            name: Workout name.
            category: Workout category.
            subcategory: Workout subcategory.

        """
        parser = Lark(ZWOG_GRAMMAR, start="workout", maybe_placeholders=False)

        self._name = name
        self._author = author
        self._category = category
        self._subcategory = subcategory

        self._workout: List[Block] = WorkoutTransformer().transform(
            parser.parse(workout)
        )
        self._pretty_workout = self._to_pretty(self._workout)
        self._zwo_workout = self._to_zwo(self._workout)
        self._tss = self._to_tss(self._workout)

    def save_zwo(self, filename: str) -> None:
        """Save the workout in the ZWO format.

        Args:
            filename: Filename.

        """
        self._zwo_workout.write(filename)

    def __str__(self) -> str:
        """Return str."""
        return self._pretty_workout

    @property
    def tss(self) -> float:
        """Get TSS."""
        return self._tss

    @property
    def workout(self) -> List[Block]:
        """Return workout."""
        return self._workout

    @property
    def zwo_workout(self) -> str:
        """Get the workout as ZWO."""
        return tostring(self.element_workout, encoding="unicode") + "\n"

    @property
    def element_workout(self) -> Element:
        """Get the workout as element."""
        return self._zwo_workout.getroot()

    @staticmethod
    def _is_ramp(block: Block) -> bool:
        """Check whether the block is a ramp block.

        Args:
            block: Block.

        Returns:
            True if a ramp, False otherwise.

        """
        return len(block.intervals) == 1 and isinstance(block.intervals[0].power, list)

    @staticmethod
    def _is_steady_state(block: Block) -> bool:
        """Check whether the block is a steady-state block.

        Args:
            block: Block.

        Returns:
            True if a steady-state, False otherwise.

        """
        return len(block.intervals) == 1 and not isinstance(
            block.intervals[0].power, list
        )

    @staticmethod
    def _is_intervalst(block: Block) -> bool:
        """Check whether the block is an intervalst.

        Args:
            block: Block.

        Returns:
            True if an intervalst , False otherwise.

        """
        return (
            len(block.intervals) == INTERVALST_LENGTH
            and not isinstance(block.intervals[0].power, list)
            and not isinstance(block.intervals[1].power, list)
        )

    @staticmethod
    def _interval_to_xml(
        interval: Union[Interval, List[Interval]], repeats: int = 1
    ) -> Element:
        """Return the interval as a XML node.

        Args:
            interval: The interval.
            repeats: Number of repeats.

        Returns:
            XML node representing the interval.

        """
        if isinstance(interval, Interval):
            if not isinstance(interval.power, list):  # steady-state
                element = Element("SteadyState")
                element.set("Duration", str(interval.duration))
                element.set("Power", str(interval.power / 100))
            else:  # ramp
                element = Element("Ramp")
                element.set("Duration", str(interval.duration))
                element.set("PowerLow", str(interval.power[0] / 100))
                element.set("PowerHigh", str(interval.power[1] / 100))
        elif (
            isinstance(interval, list)
            and isinstance(interval[0].power, float)
            and isinstance(interval[1].power, float)
        ):  # intervalst
            element = Element("IntervalsT")
            element.set("Repeat", str(repeats))
            element.set("OnDuration", str(interval[0].duration))
            element.set("OnPower", str(interval[0].power / 100))
            element.set("OffDuration", str(interval[1].duration))
            element.set("OffPower", str(interval[1].power / 100))
        else:
            msg = f"Unexpected interval: {interval}"
            raise TypeError(msg)
        return element

    def _to_zwo(self, blocks: List[Block]) -> ElementTree:
        """Convert to ZWO.

        See: https://github.com/h4l/zwift-workout-file-reference/blob/master/zwift_workout_file_tag_reference.md

        Args:
            blocks: Blocks.

        Returns:
            XML tree representing the workout.

        """
        root = Element("workout_file")

        # fill metadata
        for child, value in [
            ("author", self._author),
            ("name", self._name),
            (
                "description",
                (
                    "This workout was generated using ZWOG.\n\n"
                    f"{self._to_pretty(blocks)}"
                ),
            ),
            ("sportType", "bike"),
            ("category", self._category),
            ("subcategory", self._subcategory),
        ]:
            if value is not None:
                tmp = SubElement(root, child)
                tmp.text = value

        tmp = SubElement(root, "workout")
        for block_idx, block in enumerate(blocks):
            # warmup and ramp
            if block_idx in {0, (len(blocks) - 1)} and self._is_ramp(block):
                element = self._interval_to_xml(block.intervals[0])
                element.tag = "Warmup" if block_idx == 0 else "Cooldown"
                tmp.append(element)
            # ramp or steady state
            elif self._is_ramp(block) or self._is_steady_state(block):
                for _ in range(block.repeats):
                    tmp.append(self._interval_to_xml(block.intervals[0]))
            # intervalst
            elif self._is_intervalst(block):
                tmp.append(
                    self._interval_to_xml(block.intervals, repeats=block.repeats)
                )
            # non intervalst
            else:
                for _ in range(block.repeats):
                    for interval in block.intervals:
                        tmp.append(self._interval_to_xml(interval))
        return ElementTree(root)

    @staticmethod
    def _duration_to_pretty_str(duration: int) -> str:
        """Prettify and stringify duration given in seconds.

        Args:
            duration: Duration in seconds.

        Returns:
            Prettified and stringified duration.

        """

        def get_hours(duration: int) -> str:
            return (
                f"{int(duration/SECONDS_IN_HOUR)}h"
                if int(duration / SECONDS_IN_HOUR) > 0
                else ""
            )

        def get_minutes(duration: int) -> str:
            return (
                f"{int((duration % SECONDS_IN_HOUR)/SECONDS_IN_MINUTE)}m"
                if int((duration % SECONDS_IN_HOUR) / SECONDS_IN_MINUTE)
                else ""
            )

        def get_seconds(duration: int) -> str:
            return (
                f"{int(duration % SECONDS_IN_MINUTE)}s"
                if duration % SECONDS_IN_MINUTE > 0
                else ""
            )

        return get_hours(duration) + get_minutes(duration) + get_seconds(duration)

    def _interval_to_str(self, interval: Interval) -> str:
        """Return the interval as a string.

        Args:
            interval: Interval.

        Returns:
            String representation of the interval.

        """
        if isinstance(interval.power, list):
            return (
                f"{self._duration_to_pretty_str(interval.duration)}"
                f" from {interval.power[0]:.0f} to "
                f"{interval.power[1]:.0f}% FTP"
            )
        return (
            f"{self._duration_to_pretty_str(interval.duration)} "
            f"@ {interval.power:.0f}% FTP"
        )

    @staticmethod
    def _interval_to_tss(interval: Interval) -> float:
        """Calculate TSS for an interval.

        Args:
            interval: Interval.

        Returns:
            Calculated TSS.

        """
        if isinstance(interval.power, list):
            min_power = min([interval.power[0], interval.power[1]])
            max_power = max([interval.power[0], interval.power[1]])
        else:
            min_power = interval.power
            max_power = interval.power
        return (
            interval.duration / 3600 * min_power
            + interval.duration / 3600 * (max_power - min_power) / 2
        )

    def _to_pretty(self, blocks: List[Block]) -> str:
        """Return the workout as a string.

        Args:
            blocks: Workout.

        Returns:
            str: String representation of the workout.

        """
        return "\n".join(
            (f"{block.repeats}x " if block.repeats > 1 else "")
            + ", ".join(
                [self._interval_to_str(interval) for interval in block.intervals]
            )
            for block in blocks
        )

    def _to_tss(self, blocks: List[Block]) -> float:
        """Calculate TSS for a workout.

        Args:
            blocks: Workout.

        Returns:
            Calculated TSS.

        """
        return sum(
            self._interval_to_tss(block.intervals[0])
            if self._is_ramp(block) or self._is_steady_state(block)
            else sum(
                block.repeats * self._interval_to_tss(interval)
                for interval in block.intervals
            )
            for block in blocks
        )


def main() -> NoReturn:
    """ZWOG command line interface."""
    parser = argparse.ArgumentParser(description="Zwift workout generator")

    parser.add_argument(
        "-i",
        "--input_file",
        nargs="?",
        action="store",
        dest="input_file",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="input filename",
    )
    parser.add_argument(
        "-o",
        "--output_file",
        nargs="?",
        action="store",
        dest="output_file",
        type=argparse.FileType("w"),
        default=sys.stdout,
        help="output filename",
    )
    parser.add_argument(
        "-a",
        "--author",
        action="store",
        dest="author",
        type=str,
        default="Zwift workout generator (https://github.com/tare/zwog)",
        required=False,
        help="author name",
    )
    parser.add_argument(
        "-n",
        "--name",
        action="store",
        dest="name",
        type=str,
        default="Structured workout",
        required=False,
        help="workout name",
    )
    parser.add_argument(
        "-c",
        "--category",
        action="store",
        dest="category",
        type=str,
        default=None,
        required=False,
        help="category",
    )
    parser.add_argument(
        "-s",
        "--subcategory",
        action="store",
        dest="subcategory",
        type=str,
        default=None,
        required=False,
        help="subcategory",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"zwog {version('zwog')}",
    )

    options = parser.parse_args()

    with options.input_file:
        workout_text = options.input_file.read()

    workout = ZWOG(
        workout_text,
        options.author,
        options.name,
        options.category,
        options.subcategory,
    )

    with options.output_file:
        options.output_file.write(workout.zwo_workout)

    sys.exit(0)
