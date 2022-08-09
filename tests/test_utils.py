"""unit tests for zwog.utils."""
import xml.etree.ElementTree as ET

import pytest
from lark.exceptions import UnexpectedCharacters, UnexpectedEOF

from zwog.utils import ZWOG, WorkoutTransformer


def elements_equal(e1, e2):
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
    return all(elements_equal(c1, c2) for c1, c2 in zip(e1, e2))


def test_zwog_grammar():
    """Test grammar."""
    with pytest.raises(UnexpectedCharacters):
        ZWOG("x")
    with pytest.raises(UnexpectedCharacters):
        ZWOG(r"1 @ 50% FTP")
    with pytest.raises(UnexpectedEOF):
        ZWOG(r"1h @ 50%")
    with pytest.raises(UnexpectedCharacters):
        ZWOG(r"1h 50% FTP")
    with pytest.raises(UnexpectedCharacters):
        ZWOG(r"1h @ 50 FTP")
    with pytest.raises(UnexpectedCharacters):
        ZWOG(r",1h @ 50% FTP")
    with pytest.raises(UnexpectedCharacters):
        ZWOG(r"1h from 10 to 50 FTP")
    with pytest.raises(UnexpectedCharacters):
        ZWOG(r"1h @ 10 to 50% FTP")
    with pytest.raises(UnexpectedCharacters):
        ZWOG(r"1h from 10% to 50% FTP")
    with pytest.raises(UnexpectedCharacters):
        ZWOG(r"2x 1h from 10 to 50% FTP, 2x 1h @ 50% FTP")
    with pytest.raises(UnexpectedCharacters):
        ZWOG(r"1x from 10 to 50% FTP")
    with pytest.raises(UnexpectedCharacters):
        ZWOG(r"1f from 10 to 50% FTP")


def test_duration():
    """Test duration."""
    assert WorkoutTransformer().duration([10, "h"]) == 36000
    assert WorkoutTransformer().duration([10, "m"]) == 600
    assert WorkoutTransformer().duration([10, "s"]) == 10

    with pytest.raises(ValueError):
        WorkoutTransformer().duration([10, "x"])


def test_durations():
    """Test durations."""
    assert WorkoutTransformer().durations([10, 20]) == 30


def test_steady_state():
    """Test steady_state."""
    assert WorkoutTransformer().steady_state([10, 100.0]) == {
        "duration": 10,
        "power": 100.0,
    }


def test_ramp():
    """Test ramp."""
    assert WorkoutTransformer().ramp([10, [100.0, 200.0]]) == {
        "duration": 10,
        "power": [100.0, 200.0],
    }


def test_power():
    """Test power."""
    assert WorkoutTransformer().power([100.0]) == 100.0
    assert WorkoutTransformer().power([100.0, 200.0]) == [100.0, 200.0]


def test_repeats():
    """Test repeats."""
    assert WorkoutTransformer().repeats([1]) == ("repeats", 1)
    assert WorkoutTransformer().repeats([2]) == ("repeats", 2)


def test_intervals():
    """Test intervals."""
    assert WorkoutTransformer().intervals([1, 2]) == ("intervals", [1, 2])


def test_block():
    """Test block."""
    assert (
        WorkoutTransformer().block(
            [("intervals", [{"duration": 600, "power": 50.0}])]
        )
    ) == {"intervals": [{"duration": 600, "power": 50.0}]}


def test_zwog_str():
    """Test __str__ (ZWOG)."""
    assert str(ZWOG(r"55s @ 100% FTP")) == r"55s @ 100% FTP"
    assert str(ZWOG(r"1h60s @ 100% FTP")) == r"1h1m @ 100% FTP"
    assert str(ZWOG(r"1hrs60sec @ 100% FTP")) == r"1h1m @ 100% FTP"
    assert str(ZWOG(r"2min @ 100% FTP")) == r"2m @ 100% FTP"
    assert str(ZWOG(r"60sec @ 100% FTP")) == r"1m @ 100% FTP"
    assert (
        str(ZWOG(r"1h1hrs1m 1min1sec  1sec @ 100% FTP"))
        == r"2h2m2s @ 100% FTP"
    )
    assert (
        str(ZWOG(r"150s from 50 to 100%     FTP"))
        == r"2m30s from 50 to 100% FTP"
    )
    assert (
        str(ZWOG(r"150s from 50 to 100% FTP 2m @ 50% FTP"))
        == "2m30s from 50 to 100% FTP\n2m @ 50% FTP"
    )
    assert (
        str(ZWOG(r"150s from 50 to 100% FTP, 2m @ 50% FTP"))
        == "2m30s from 50 to 100% FTP, 2m @ 50% FTP"
    )
    assert (
        str(ZWOG(r"3x 150s from 50 to 100% FTP"))
        == "3x 2m30s from 50 to 100% FTP"
    )
    assert (
        str(
            ZWOG(
                (
                    r"3 x 150s from 50 to 100% FTP, "
                    r"2m @ 50% FTP 5s @ 10  %   FTP  "
                )
            )
        )
        == "3x 2m30s from 50 to 100% FTP, 2m @ 50% FTP\n5s @ 10% FTP"
    )


def test_tss():
    """Test tss (ZWOG)."""
    assert ZWOG(r"60s @ 100% FTP").tss == 100 / 60
    assert ZWOG(r"60s from 0 to 100% FTP").tss == 100 / 60 / 2
    assert ZWOG(r"1h @ 66% FTP, 1h @ 100% FTP").tss == 166.0
    assert ZWOG(r"").tss == 0.0


def test_json_workout():
    """Test json_workout (ZWOG)."""
    assert ZWOG(r"60s @ 100% FTP").json_workout == [
        {"intervals": [{"duration": 60, "power": 100.0}]}
    ]
    assert ZWOG(r"4x 60s @ 100% FTP").json_workout == [
        {"repeats": 4, "intervals": [{"duration": 60, "power": 100.0}]}
    ]
    assert ZWOG(r"4x 60s from 10 to 100% FTP").json_workout == [
        {"repeats": 4, "intervals": [{"duration": 60, "power": [10.0, 100.0]}]}
    ]
    assert ZWOG(
        (r"4x 60s from 10 to 100% FTP, " r"20s @ 70% FTP")
    ).json_workout == [
        {
            "repeats": 4,
            "intervals": [
                {"duration": 60, "power": [10.0, 100.0]},
                {"duration": 20, "power": 70.0},
            ],
        }
    ]
    assert ZWOG(r"4x 50s from 10 to 100% FTP 2h @ 90% FTP").json_workout == [
        {
            "repeats": 4,
            "intervals": [{"duration": 50, "power": [10.0, 100.0]}],
        },
        {"intervals": [{"duration": 7200, "power": 90.0}]},
    ]


def test_zwo_workout():
    """Test zwo_workout (ZWOG)."""
    assert elements_equal(
        ZWOG(r"10m @ 50% FTP", "John Dow", "Cat1", "SubCat1").element_workout,
        ET.ElementTree(
            ET.fromstring(
                "<workout_file><author>John Dow</author><name>Cat1</name>"
                "<description>This workout was generated using ZWOG.\n\n"
                "10m @ 50% FTP</description><sportType>bike</sportType>"
                "<category>SubCat1</category><workout>"
                '<SteadyState Duration="600" Power="0.5" />'
                "</workout></workout_file>\n"
            )
        ).getroot(),
    )

    assert elements_equal(
        ZWOG(
            (
                r"60s from 40 to 80% FTP 10m @ 80% FTP "
                r"10min from 80 to 70% FTP 1h from 70 to 50% FTP"
            ),
            "John Dow",
            "Cat1",
            "SubCat1",
        ).element_workout,
        ET.ElementTree(
            ET.fromstring(
                "<workout_file><author>John Dow</author><name>Cat1"
                "</name><description>This workout was generated using "
                "ZWOG.\n\n1m from 40 to 80% FTP\n10m @ 80% FTP\n10m "
                "from 80 to 70% FTP\n1h from 70 to 50% FTP"
                "</description><sportType>bike</sportType>"
                "<category>SubCat1</category><workout><Warmup "
                'Duration="60" PowerLow="0.4" PowerHigh="0.8" '
                '/><SteadyState Duration="600" Power="0.8" '
                '/><Ramp Duration="600" PowerLow="0.8" '
                'PowerHigh="0.7" /><Cooldown Duration="3600" '
                'PowerLow="0.7" PowerHigh="0.5" /></workout>'
                "</workout_file>\n"
            )
        ).getroot(),
    )

    assert elements_equal(
        ZWOG(
            (
                r"1m @ 50% FTP 3x 5 min from 70 to 100% FTP, "
                r"5 min from 100 to 70% FTP 1m @ 50% FTP"
            ),
            "John Dow",
            "Cat1",
            "SubCat1",
        ).element_workout,
        ET.ElementTree(
            ET.fromstring(
                "<workout_file><author>John Dow</author><name>Cat1</name>"
                "<description>This workout was generated using ZWOG.\n\n"
                "1m @ 50% FTP\n3x 5m from 70 to 100% FTP, 5m from 100 "
                "to 70% FTP\n1m @ 50% FTP</description><sportType>bike"
                "</sportType><category>SubCat1</category><workout>"
                '<SteadyState Duration="60" Power="0.5" /><Ramp '
                'Duration="300" PowerLow="0.7" PowerHigh="1.0" />'
                '<Ramp Duration="300" PowerLow="1.0" PowerHigh="0.7" '
                '/><Ramp Duration="300" PowerLow="0.7" PowerHigh="1.0" '
                '/><Ramp Duration="300" PowerLow="1.0" PowerHigh="0.7" '
                '/><Ramp Duration="300" PowerLow="0.7" PowerHigh="1.0" '
                '/><Ramp Duration="300" PowerLow="1.0" PowerHigh="0.7" '
                '/><SteadyState Duration="60" Power="0.5" /></workout>'
                "</workout_file>\n"
            )
        ).getroot(),
    )
