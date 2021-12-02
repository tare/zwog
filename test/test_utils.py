"""unit tests for zwog.utils"""
import pytest
from lark.exceptions import (UnexpectedCharacters,
                             UnexpectedEOF)

from zwog.utils import ZWOG, WorkoutTransformer

def test_zwog_grammar():
    """Tests grammar."""
    with pytest.raises(UnexpectedCharacters):
        ZWOG('x')
    with pytest.raises(UnexpectedCharacters):
        ZWOG(r'1 @ 50% FTP')
    with pytest.raises(UnexpectedEOF):
        ZWOG(r'1h @ 50%')
    with pytest.raises(UnexpectedCharacters):
        ZWOG(r'1h 50% FTP')
    with pytest.raises(UnexpectedCharacters):
        ZWOG(r'1h @ 50 FTP')
    with pytest.raises(UnexpectedCharacters):
        ZWOG(r',1h @ 50% FTP')
    with pytest.raises(UnexpectedCharacters):
        ZWOG(r'1h from 10 to 50 FTP')
    with pytest.raises(UnexpectedCharacters):
        ZWOG(r'1h @ 10 to 50% FTP')
    with pytest.raises(UnexpectedCharacters):
        ZWOG(r'1h from 10% to 50% FTP')
    with pytest.raises(UnexpectedCharacters):
        ZWOG(r'2x 1h from 10 to 50% FTP, 2x 1h @ 50% FTP')
    with pytest.raises(UnexpectedCharacters):
        ZWOG(r'1x from 10 to 50% FTP')
    with pytest.raises(UnexpectedCharacters):
        ZWOG(r'1f from 10 to 50% FTP')

def test_duration():
    """Tests duration."""
    assert WorkoutTransformer().duration([10,'h']) == 36000
    assert WorkoutTransformer().duration([10,'m']) == 600
    assert WorkoutTransformer().duration([10,'s']) == 10

    with pytest.raises(ValueError):
        WorkoutTransformer().duration([10,'x'])

def test_durations():
    """Tests durations"""
    assert WorkoutTransformer().durations([10,20]) == 30

def test_steady_state():
    """Tests steady_state."""
    assert WorkoutTransformer().steady_state([10,100.0]) == \
       {'duration':10,'power':100.0}

def test_ramp():
    """Tests ramp."""
    assert WorkoutTransformer().ramp([10,[100.0,200.0]]) == \
        {'duration':10,'power':[100.0,200.0]}

def test_power():
    """Tests power."""
    assert WorkoutTransformer().power([100.0]) == 100.0
    assert WorkoutTransformer().power([100.0,200.0]) == [100.0,200.0]

def test_repeats():
    """Tests repeats."""
    assert WorkoutTransformer().repeats([1]) == ('repeats',1)
    assert WorkoutTransformer().repeats([2]) == ('repeats',2)

def test_intervals():
    """Tests intervals."""
    assert WorkoutTransformer().intervals([1,2]) == ('intervals',[1,2])

def test_block():
    """Tests block."""
    assert (WorkoutTransformer()
            .block([('intervals',[{'duration':600,'power':50.0}])])) == \
                {'intervals':[{'duration':600,'power':50.0}]}

def test_zwog_str():
    """Tests __str__ (ZWOG)."""
    assert str(ZWOG(r'55s @ 100% FTP')) == r'55s @ 100% FTP'
    assert str(ZWOG(r'1h60s @ 100% FTP')) == r'1h1m @ 100% FTP'
    assert str(ZWOG(r'1hrs60sec @ 100% FTP')) == r'1h1m @ 100% FTP'
    assert str(ZWOG(r'2min @ 100% FTP')) == r'2m @ 100% FTP'
    assert str(ZWOG(r'60sec @ 100% FTP')) == r'1m @ 100% FTP'
    assert str(ZWOG(r'1h1hrs1m 1min1sec  1sec @ 100% FTP')) == \
        r'2h2m2s @ 100% FTP'
    assert str(ZWOG(r'150s from 50 to 100%     FTP')) == \
        r'2m30s from 50 to 100% FTP'
    assert str(ZWOG(r'150s from 50 to 100% FTP 2m @ 50% FTP')) == \
        '2m30s from 50 to 100% FTP\n2m @ 50% FTP'
    assert str(ZWOG(r'150s from 50 to 100% FTP, 2m @ 50% FTP')) == \
        '2m30s from 50 to 100% FTP, 2m @ 50% FTP'
    assert str(ZWOG(r'3x 150s from 50 to 100% FTP')) == \
        '3x 2m30s from 50 to 100% FTP'
    assert str(ZWOG((r'3 x 150s from 50 to 100% FTP, '
                     r'2m @ 50% FTP 5s @ 10  %   FTP  '))) == \
        '3x 2m30s from 50 to 100% FTP, 2m @ 50% FTP\n5s @ 10% FTP'

def test_tss():
    """Tests tss (ZWOG)."""
    assert ZWOG(r'60s @ 100% FTP').tss == 100/60
    assert ZWOG(r'60s from 0 to 100% FTP').tss == 100/60/2
    assert ZWOG(r'1h @ 66% FTP, 1h @ 100% FTP').tss == 166.0
    assert ZWOG(r'').tss == 0.0

def test_json_workout():
    """Tests json_workout (ZWOG)."""
    assert ZWOG(r'60s @ 100% FTP').json_workout == \
        [{'intervals':
        [{'duration': 60, 'power': 100.0}]}]
    assert ZWOG(r'4x 60s @ 100% FTP').json_workout == \
        [{'repeats': 4,
          'intervals': [{'duration': 60, 'power': 100.0}]}]
    assert ZWOG(r'4x 60s from 10 to 100% FTP').json_workout == \
        [{'repeats': 4,
          'intervals':[{'duration': 60, 'power': [10.0,100.0]}]}]
    assert ZWOG((r'4x 60s from 10 to 100% FTP, '
                 r'20s @ 70% FTP')).json_workout == \
        [{'repeats': 4,
          'intervals':[{'duration': 60, 'power': [10.0,100.0]},
                       {'duration': 20, 'power': 70.0}]}]
    assert ZWOG(r'4x 50s from 10 to 100% FTP 2h @ 90% FTP').json_workout == \
        [{'repeats': 4,
          'intervals': [{'duration': 50, 'power': [10.0, 100.0]}]},
         {'intervals': [{'duration': 7200, 'power': 90.0}]}]

def test_tree_workout():
    """Tests tree_workout (ZWOG)."""
    pass

def test_zwo_workout():
    """Tests zwo_workout (ZWOG)."""
    pass