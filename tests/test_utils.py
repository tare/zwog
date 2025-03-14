"""unit tests for zwog.utils."""

from itertools import starmap
from tempfile import NamedTemporaryFile
from xml.etree.ElementTree import Element, ElementTree, fromstring, parse  # noqa: S405

import pytest
from lark.exceptions import UnexpectedCharacters, UnexpectedEOF

from zwog.utils import ZWOG, Block, Interval, WorkoutTransformer


def elements_equal(e1: Element, e2: Element) -> bool:
    """Test two elements.

    Taken from: https://stackoverflow.com/a/24349916

    Args:
        e1: First element.
        e2: Second element

    Returns:
        True if equal otherwise False.

    """
    if e1.tag != e2.tag:
        return False
    if e1.text != e2.text:
        return False
    if e1.tail != e2.tail:
        return False
    if e1.attrib != e2.attrib:
        return False
    if len(e1) != len(e2):
        return False
    return all(starmap(elements_equal, zip(e1, e2, strict=True)))


@pytest.mark.parametrize(
    ("test_input", "exception"),
    [
        ("x", UnexpectedCharacters),
        (r"1 @ 50% FTP", UnexpectedCharacters),
        (r"1h @ 50%", UnexpectedEOF),
        (r"1h 50% FTP", UnexpectedCharacters),
        (r"1h @ 50 FTP", UnexpectedCharacters),
        (r",1h @ 50% FTP", UnexpectedCharacters),
        (r"1h from 10 to 50 FTP", UnexpectedCharacters),
        (r"1h @ 10 to 50% FTP", UnexpectedCharacters),
        (r"1h from 10% to 50% FTP", UnexpectedCharacters),
        (r"2x 1h from 10 to 50% FTP, 2x 1h @ 50% FTP", UnexpectedCharacters),
        (r"1x from 10 to 50% FTP", UnexpectedCharacters),
        (r"1f from 10 to 50% FTP", UnexpectedCharacters),
    ],
)
def test_zwog_grammar(test_input: str, exception: type[Exception]) -> None:
    """Test grammar."""
    with pytest.raises(exception):
        ZWOG(test_input)


@pytest.mark.parametrize(
    ("test_input", "expected"),
    [
        ([(10, "s"), (20, "sec")], 30),
        ([(10, "s"), (2, "m")], 130),
        ([(10, "s"), (0.5, "h")], 1810),
    ],
)
def test_durations(test_input: list[tuple[int | float, str]], expected: int) -> None:
    """Test durations."""
    assert WorkoutTransformer().durations(test_input) == expected


@pytest.mark.parametrize(
    ("test_input", "exception", "match"),
    [
        ([(10, "x")], ValueError, "Unexpected unit of time: x"),
        (
            [(0.5, "s")],
            ValueError,
            "Interval duration values need to be strictly positive",
        ),
        ([(0, "m")], ValueError, "Duration values need to be strictly positive"),
        ([(-10, "h")], ValueError, "Duration values need to be strictly positive"),
    ],
)
def test_durations_exceptions(
    test_input: list[tuple[int | float, str]],
    exception: type[Exception],
    match: str,
) -> None:
    """Test durations exceptions."""
    with pytest.raises(exception, match=match):
        WorkoutTransformer().durations(test_input)


@pytest.mark.parametrize(
    ("test_input", "expected"),
    [
        ([10], 10),
        ([10, 10], [10, 10]),
    ],
)
def test_power(test_input: list[float], expected: float) -> None:
    """Test power."""
    assert WorkoutTransformer().power(test_input) == expected


@pytest.mark.parametrize(
    ("test_input", "exception", "match"),
    [
        ([10, -10], ValueError, "Power values need to be positive"),
        ([-10], ValueError, "Power values need to be positive"),
    ],
)
def test_power_exceptions(
    test_input: list[float], exception: type[Exception], match: str
) -> None:
    """Test power exceptions."""
    with pytest.raises(exception, match=match):
        WorkoutTransformer().power(test_input)


@pytest.mark.parametrize(
    ("test_input", "expected"),
    [
        (
            [(10, 100.0)],
            Interval(
                duration=10,
                power=100.0,
            ),
        ),
    ],
)
def test_steady_state(
    test_input: list[tuple[int, float | list[float]]], expected: Interval
) -> None:
    """Test steady_state."""
    assert WorkoutTransformer().interval(test_input) == expected


@pytest.mark.parametrize(
    ("test_input", "expected"),
    [
        (
            [(10, [100.0, 200.0])],
            Interval(
                duration=10,
                power=[100.0, 200.0],
            ),
        ),
    ],
)
def test_ramp(
    test_input: list[tuple[int, float | list[float]]], expected: Interval
) -> None:
    """Test ramp."""
    assert WorkoutTransformer().interval(test_input) == expected


@pytest.mark.parametrize(
    ("test_input", "expected"),
    [
        (
            [1],
            (
                "repeats",
                1,
            ),
        ),
        (
            [2],
            (
                "repeats",
                2,
            ),
        ),
    ],
)
def test_repeats(test_input: list[int], expected: tuple[str, int]) -> None:
    """Test repeats."""
    assert WorkoutTransformer().repeats(test_input) == expected


@pytest.mark.parametrize(
    ("test_input", "expected"),
    [
        (
            [Interval(duration=1, power=2)],
            (
                "intervals",
                [Interval(duration=1, power=2)],
            ),
        ),
        (
            [
                Interval(
                    duration=1,
                    power=[2, 2],
                )
            ],
            (
                "intervals",
                [
                    Interval(
                        duration=1,
                        power=[2, 2],
                    )
                ],
            ),
        ),
    ],
)
def test_intervals(
    test_input: list[Interval], expected: tuple[str, list[Interval]]
) -> None:
    """Test intervals."""
    assert WorkoutTransformer().intervals(test_input) == expected


@pytest.mark.parametrize(
    ("test_input", "expected"),
    [
        (
            [
                (
                    "intervals",
                    [
                        Interval(
                            duration=600,
                            power=50.0,
                        )
                    ],
                )
            ],
            Block(intervals=[Interval(duration=600, power=50.0)]),
        ),
        (
            [
                ("repeats", 2),
                (
                    "intervals",
                    [
                        Interval(
                            duration=600,
                            power=50.0,
                        )
                    ],
                ),
            ],
            Block(repeats=2, intervals=[Interval(duration=600, power=50.0)]),
        ),
    ],
)
def test_block(
    test_input: list[tuple[str, int | list[Interval]]], expected: Block
) -> None:
    """Test block."""
    assert (WorkoutTransformer().block(test_input)) == expected


@pytest.mark.parametrize(
    ("test_input", "expected"),
    [
        (r"55s @ 100% FTP", r"55s @ 100% FTP"),
        (r"1h60s @ 100% FTP", r"1h1m @ 100% FTP"),
        (r"1hrs60sec @ 100% FTP", r"1h1m @ 100% FTP"),
        (r"2min @ 100% FTP", r"2m @ 100% FTP"),
        (r"60sec @ 100% FTP", r"1m @ 100% FTP"),
        (r"1h1hrs1m 1min1sec  1sec @ 100% FTP", r"2h2m2s @ 100% FTP"),
        (r"150s from 50 to 100%     FTP", r"2m30s from 50 to 100% FTP"),
        (
            r"150s from 50 to 100% FTP 2m @ 50% FTP",
            "2m30s from 50 to 100% FTP\n2m @ 50% FTP",
        ),
        (
            r"150s from 50 to 100% FTP, 2m @ 50% FTP",
            "2m30s from 50 to 100% FTP, 2m @ 50% FTP",
        ),
        (r"3x 150s from 50 to 100% FTP", "3x 2m30s from 50 to 100% FTP"),
        (
            r"3 x 150s from 50 to 100% FTP, 2m @ 50% FTP 5s @ 10  %   FTP  ",
            "3x 2m30s from 50 to 100% FTP, 2m @ 50% FTP\n5s @ 10% FTP",
        ),
    ],
)
def test_zwog_str(test_input: str, expected: str) -> None:
    """Test __str__ (ZWOG)."""
    assert str(ZWOG(test_input)) == expected


@pytest.mark.parametrize(
    ("test_input", "expected"),
    [
        (r"60s @ 100% FTP", 100 / 60),
        (r"60s from 0 to 100% FTP", 100 / 60 / 2),
        (r"1h @ 66% FTP, 1h @ 100% FTP", 166.0),
        (r"", 0.0),
    ],
)
def test_tss(test_input: str, expected: float) -> None:
    """Test tss (ZWOG)."""
    assert ZWOG(test_input).tss == expected


@pytest.mark.parametrize(
    ("test_input", "expected"),
    [
        (
            r"60s @ 100% FTP",
            [
                Block(
                    intervals=[
                        Interval(
                            duration=60,
                            power=100.0,
                        )
                    ]
                )
            ],
        ),
        (
            r"4x 60s @ 100% FTP",
            [
                Block(
                    repeats=4,
                    intervals=[
                        Interval(
                            duration=60,
                            power=100.0,
                        )
                    ],
                )
            ],
        ),
        (
            r"4x 60s from 10 to 100% FTP",
            [
                Block(
                    repeats=4,
                    intervals=[
                        Interval(
                            duration=60,
                            power=[10.0, 100.0],
                        )
                    ],
                )
            ],
        ),
        (
            r"4x 60s from 10 to 100% FTP, 20s @ 70% FTP",
            [
                Block(
                    repeats=4,
                    intervals=[
                        Interval(
                            duration=60,
                            power=[10.0, 100.0],
                        ),
                        Interval(
                            duration=20,
                            power=70.0,
                        ),
                    ],
                )
            ],
        ),
        (
            r"4x 50s from 10 to 100% FTP 2h @ 90% FTP",
            [
                Block(
                    repeats=4,
                    intervals=[
                        Interval(
                            duration=50,
                            power=[10.0, 100.0],
                        )
                    ],
                ),
                Block(
                    intervals=[
                        Interval(
                            duration=7200,
                            power=90.0,
                        )
                    ]
                ),
            ],
        ),
    ],
)
def test_workout(test_input: str, expected: list[Block]) -> None:
    """Test workout (ZWOG)."""
    assert ZWOG(test_input).workout == expected


@pytest.mark.parametrize(
    ("test_input", "expected"),
    [
        (
            [r"10m @ 50% FTP", "John Dow", "Cat1", "SubCat1"],
            (
                """<workout_file><author>John Dow</author><name>Cat1</name><description>This workout was generated using ZWOG.

10m @ 50% FTP</description><sportType>bike</sportType><category>SubCat1</category><workout><SteadyState Duration="600" Power="0.5" /></workout></workout_file>
"""
            ),
        ),
        (
            [r"2 x 1m @ 95% FTP, 2m @ 105% FTP", "John Dow", "Cat1", "SubCat1"],
            (
                """<workout_file><author>John Dow</author><name>Cat1</name><description>This workout was generated using ZWOG.

2x 1m @ 95% FTP, 2m @ 105% FTP</description><sportType>bike</sportType><category>SubCat1</category><workout><IntervalsT Repeat="2" OnDuration="60" OnPower="0.95" OffDuration="120" OffPower="1.05" /></workout></workout_file>
"""
            ),
        ),
        (
            [
                (
                    r"60s from 40 to 80% FTP 10m @ 80% FTP "
                    r"10min from 80 to 70% FTP 1h from 70 to 50% FTP"
                ),
                "John Dow",
                "Cat1",
                "SubCat1",
            ],
            (
                """<workout_file><author>John Dow</author><name>Cat1</name><description>This workout was generated using ZWOG.

1m from 40 to 80% FTP
10m @ 80% FTP
10m from 80 to 70% FTP
1h from 70 to 50% FTP</description><sportType>bike</sportType><category>SubCat1</category><workout><Warmup Duration="60" PowerLow="0.4" PowerHigh="0.8"/><SteadyState Duration="600" Power="0.8" /><Ramp Duration="600" PowerLow="0.8" PowerHigh="0.7" /><Cooldown Duration="3600" PowerLow="0.7" PowerHigh="0.5" /></workout></workout_file>
"""
            ),
        ),
        (
            [
                (
                    r"1m @ 50% FTP 3x 5 min from 70 to 100% FTP, "
                    r"5 min from 100 to 70% FTP 1m @ 50% FTP"
                ),
                "John Dow",
                "Cat1",
                "SubCat1",
            ],
            (
                """<workout_file><author>John Dow</author><name>Cat1</name><description>This workout was generated using ZWOG.

1m @ 50% FTP
3x 5m from 70 to 100% FTP, 5m from 100 to 70% FTP
1m @ 50% FTP</description><sportType>bike</sportType><category>SubCat1</category><workout><SteadyState Duration="60" Power="0.5" /><Ramp Duration="300" PowerLow="0.7" PowerHigh="1.0" /><Ramp Duration="300" PowerLow="1.0" PowerHigh="0.7" /><Ramp Duration="300" PowerLow="0.7" PowerHigh="1.0" /><Ramp Duration="300" PowerLow="1.0" PowerHigh="0.7" /><Ramp Duration="300" PowerLow="0.7" PowerHigh="1.0" /><Ramp Duration="300" PowerLow="1.0" PowerHigh="0.7" /><SteadyState Duration="60" Power="0.5" /></workout></workout_file>
"""
            ),
        ),
    ],
)
def test_element_workout(test_input: list[str], expected: str) -> None:
    """Test element_workout (ZWOG)."""
    assert elements_equal(
        ZWOG(*test_input).element_workout,
        ElementTree(fromstring(expected)).getroot(),  # noqa: S314
    )


@pytest.mark.parametrize(
    "test_input",
    [r"4x 50s from 10 to 100% FTP 2h @ 90% FTP"],
)
def test_save_zwo(test_input: str) -> None:
    """Test save_zwo (ZWOG)."""
    workout = ZWOG(test_input)
    with NamedTemporaryFile(suffix=".xml") as tmp_file:
        workout.save_zwo(tmp_file.name)
        read_workout = parse(tmp_file.name)  # noqa: S314
    assert elements_equal(
        read_workout.getroot(),
        workout.element_workout,
    )


@pytest.mark.parametrize(
    ("test_input", "expected"),
    [
        (
            [
                r"10m @ 50% FTP",
                "John Dow",
                "Cat1",
                "SubCat1",
            ],
            (
                """<workout_file><author>John Dow</author><name>Cat1</name><description>This workout was generated using ZWOG.

10m @ 50% FTP</description><sportType>bike</sportType><category>SubCat1</category><workout><SteadyState Duration="600" Power="0.5" /></workout></workout_file>
"""
            ),
        ),
        (
            [
                r"70s @ 50% FTP",
                "John Dow",
                "Cat1",
                "SubCat1",
            ],
            (
                """<workout_file><author>John Dow</author><name>Cat1</name><description>This workout was generated using ZWOG.

1m10s @ 50% FTP</description><sportType>bike</sportType><category>SubCat1</category><workout><SteadyState Duration="70" Power="0.5" /></workout></workout_file>
"""
            ),
        ),
        (
            [
                r"2h 70m 70 s @ 50% FTP",
                "John Dow",
                "Cat1",
                "SubCat1",
            ],
            (
                """<workout_file><author>John Dow</author><name>Cat1</name><description>This workout was generated using ZWOG.

3h11m10s @ 50% FTP</description><sportType>bike</sportType><category>SubCat1</category><workout><SteadyState Duration="11470" Power="0.5" /></workout></workout_file>
"""
            ),
        ),
    ],
)
def test_zwo_workout(test_input: list[str], expected: str) -> None:
    """Test zwo_workout (ZWOG)."""
    assert ZWOG(*test_input).zwo_workout == expected
