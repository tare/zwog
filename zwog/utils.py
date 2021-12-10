"""Routines for processing workouts."""
from typing import Union, Tuple, Optional
from xml.etree.ElementTree import (ElementTree, Element,
                                   SubElement, tostring)

from lark import Lark
from lark import Transformer


class WorkoutTransformer(Transformer):
    """Class to process workout parse-trees."""

    def duration(self, d: list) -> int:
        """Return duration in seconds."""
        if d[1] == 'hrs' or d[1] == 'h':
            # return duration in seconds
            return int(d[0]*3600)
        elif d[1] == 'min' or d[1] == 'm':
            # return duration in seconds
            return int(d[0]*60)
        elif d[1] == 'sec' or d[1] == 's':
            return int(d[0])
        else:
            # this should not happen
            raise ValueError(f'Unexpected unit of time: {d[1]}')

    def durations(self, d: list) -> int:
        """Return total duration."""
        return sum(d)

    def steady_state(self, s: list) -> dict:
        """Return steady-state."""
        return dict(duration=s[0], power=s[1])

    def ramp(self, s: list) -> dict:
        """Return ramp."""
        return dict(duration=s[0], power=s[1])

    def power(self, p: list[float]) -> Union[float, list]:
        """Return power."""
        if len(p) == 1:
            return p[0]
        else:
            return p

    def repeats(self, r: list) -> Tuple[str, int]:
        """Return repeats."""
        return 'repeats', r[0]

    def intervals(self, i: list) -> Tuple[str, list]:
        """Return intervals."""
        return 'intervals', i

    def block(self, b: list) -> dict:
        """Return block."""
        return dict(b)

    INT = int
    NUMBER = float
    TIME_UNIT = str
    workout = list


class ZWOG():
    """Zwift workout generator (ZWOG)."""

    def __init__(self, workout: str,
                 author: str = ('Zwift workout generator '
                                '(https://github.com/tare/zwog)'),
                 name: str = 'Structured workout',
                 category: Optional[str] = None,
                 subcategory: Optional[str] = None):
        """Initialize ZWOG.

        Args:
            workout: Workout as a string.
            author: Author.
            name: Workout name.
            category: Workout category.
            subcategory: Workout subcategory.

        """
        parser = Lark(r"""
            workout: block*
            block: [repeats "x"] intervals
            intervals: (ramp|steady_state)~1 ("," (steady_state|ramp))*
            steady_state: durations "@" steady_state_power "%" "FTP"
            ramp: durations "from" ramp_power "%" "FTP"
            durations: duration+
            duration: NUMBER TIME_UNIT
            time_unit: TIME_UNIT
            TIME_UNIT: ("sec"|"s"|"min"|"m"|"hrs"|"h")
            repeats: INT
            steady_state_power: NUMBER -> power
            ramp_power: NUMBER "to" NUMBER -> power

            %ignore WS
            %import common.WS
            %import common.INT
            %import common.NUMBER
        """, start='workout')

        self.__name = name
        self.__author = author
        self.__category = category
        self.__subcategory = subcategory

        # self.__tree_workout = parser.parse(workout)
        self.__json_workout = (WorkoutTransformer()
                               .transform(parser.parse(workout)))
        self.__pretty_workout = self._json_to_pretty(self.__json_workout)
        self.__zwo_workout = self._json_to_zwo(self.__json_workout)
        self.__tss = self._json_to_tss(self.__json_workout)

    def save_zwo(self, filename) -> None:
        """Save the workout in the ZWO format.

        Args:
            filename: Filename.

        """
        self.__zwo_workout.write(filename)

    def __str__(self):
        """Return str."""
        return self.__pretty_workout

    @property
    def tss(self) -> float:
        """Get TSS."""
        return self.__tss

    @property
    def json_workout(self) -> list[dict]:
        """Return workout as JSON."""
        return self.__json_workout

    # @property
    # def _tree_workout(self) -> str:
    #     """"""
    #     return self.__tree_workout.pretty()

    @property
    def zwo_workout(self) -> str:
        """Get the workout as ZWO."""
        return tostring(self.__zwo_workout.getroot(),
                        encoding='unicode')+'\n'

    def _is_ramp(self, block: dict) -> bool:
        """Tell whether the block is a ramp block.

        Args:
            block: Block.

        Returns:
            True if a ramp, False otherwise.

        """
        return bool(len(block['intervals']) == 1 and
                    isinstance(block['intervals'][0]['power'],
                               list))

    def _is_steady_state(self, block: dict) -> bool:
        """Tell whether the block is a steady-state block.

        Args:
            block: Block.

        Returns:
            True if a steady-state, False otherwise.

        """
        return bool(len(block['intervals']) == 1 and not
                    isinstance(block['intervals'][0]['power'],
                               list))

    def _is_intervalst(self, block: dict) -> bool:
        """Tell whether the block is an intervalst.

        Args:
            block: Block.

        Returns:
            True if an intervalst , False otherwise.

        """
        return bool(len(block['intervals']) == 2 and not
                    isinstance(block['intervals'][0]['power'], list) and not
                    isinstance(block['intervals'][1]['power'], list))

    def _interval_to_xml(self, interval: dict,
                         repeats: int = 1) -> Element:
        """Return the interval as a XML node.

        Args:
            interval: The interval.
            repeats: Number of repeats.

        Returns:
            XML node representing the interval.

        """
        if not isinstance(interval, list):
            if not isinstance(interval['power'], list):  # steady-state
                element = Element('SteadyState')
                element.set('Duration', str(interval['duration']))
                element.set('Power', str(interval['power']/100))
            else:  # ramp
                element = Element('Ramp')
                element.set('Duration', str(interval['duration']))
                element.set('PowerLow', str(interval['power'][0]/100))
                element.set('PowerHigh', str(interval['power'][1]/100))
        else:  # intervalst
            element = Element('IntervalsT')
            element.set('Repeat', str(repeats))
            element.set('OnDuration', str(interval[0]['duration']))
            element.set('OnPower', str(interval[0]['power']/100))
            element.set('OffDuration', str(interval[1]['duration']))
            element.set('OffPower', str(interval[1]['power']/100))
        return element

    def _json_to_zwo(self, blocks: list[dict]) -> ElementTree:
        """Convert JSON to ZWO.

        See: https://github.com/h4l/zwift-workout-file-reference/blob/master/zwift_workout_file_tag_reference.md

        Args:
            blocks: Blocks.

        Returns:
            XML tree representing the workout.

        """  # pylint: disable=line-too-long  # noqa
        root = Element('workout_file')

        # fill metadata
        for child, value in [('author', self.__author),
                             ('name', self.__name),
                             ('description',
                              ('This workout was generated using ZWOG.\n\n'
                               f'{self._json_to_pretty(blocks)}')),
                             ('sportType', 'bike'),
                             ('category', self.__category),
                             ('subcategory', self.__subcategory)]:
            if value is not None:
                tmp = SubElement(root, child)
                tmp.text = value

        tmp = SubElement(root, 'workout')
        for block_idx, block in enumerate(blocks):
            # warmup and ramp
            if block_idx in [0, (len(blocks)-1)] and self._is_ramp(block):
                element = self._interval_to_xml(block['intervals'][0])
                if block_idx == 0:
                    element.tag = 'Warmup'
                else:
                    element.tag = 'Cooldown'
                tmp.append(element)
            else:
                # ramp or steady state
                if self._is_ramp(block) or self._is_steady_state(block):
                    tmp.append(self._interval_to_xml(block['intervals'][0]))
                else:
                    if 'repeats' in block:
                        repeats = block['repeats']
                    else:
                        repeats = 1
                    if self._is_intervalst(block):  # intervalst
                        tmp.append(self._interval_to_xml(block['intervals'],
                                                         repeats=repeats))
                    else:  # non intervalst
                        for _ in range(repeats):
                            for interval in block['intervals']:
                                tmp.append(self._interval_to_xml(interval))
        tree = ElementTree(root)
        return tree

    def _duration_to_pretty_str(self, duration: int) -> str:
        """Prettify and stringify duration given in seconds.

        Args:
            duration: Duration in seconds.

        Returns:
            Prettified and stringified duration.

        """
        pretty_str = ''
        if int(duration/3600) > 0:
            pretty_str += f'{int(duration/3600)}h'
        if int((duration % 3600)/60) > 0:
            pretty_str += f'{int((duration % 3600)/60)}m'
        if duration % 60 > 0:
            pretty_str += f'{int((duration % 60))}s'
        return pretty_str

    def _interval_to_str(self, interval: dict) -> str:
        """Return the interval as a string.

        Args:
            interval: Interval.

        Returns:
            String representation of the interval.

        """
        if isinstance(interval['power'], list):
            return (f'{self._duration_to_pretty_str(interval["duration"])}'
                    f' from {interval["power"][0]:.0f} to '
                    f'{interval["power"][1]:.0f}% FTP')
        else:
            return (f'{self._duration_to_pretty_str(interval["duration"])} '
                    f'@ {interval["power"]:.0f}% FTP')

    def _interval_to_tss(self, interval: dict) -> float:
        """Calculate TSS for an interval.

        Args:
            interval: Interval.

        Returns:
            Calculated TSS.

        """
        if isinstance(interval['power'], list):
            min_power = min([interval['power'][0], interval['power'][1]])
            max_power = max([interval['power'][0], interval['power'][1]])
            tss = interval['duration']/3600*min_power
            tss += interval['duration']/3600*(max_power-min_power)/2
        else:
            tss = interval['duration']/3600*interval['power']
        return tss

    def _json_to_pretty(self, blocks: list[dict]) -> str:
        """Return the workout as a string.

        Args:
            blocks (list[dict]): Workout.

        Returns:
            str: String representation of the workout.

        """
        output = []
        for block in blocks:
            tmp = ''
            if 'repeats' in block:
                tmp = f'{block["repeats"]}x '
            output.append(tmp + ', '.join([
                self._interval_to_str(interval)
                for interval in block['intervals']]))
        return '\n'.join(output)

    def _json_to_tss(self, blocks: list[dict]) -> float:
        """Calculate TSS for a workout.

        Args:
            blocks: Workout.

        Returns:
            float: Calculated TSS.

        """
        tss = 0
        for block in blocks:
            # ramp or steady state
            if self._is_ramp(block) or self._is_steady_state(block):
                tss += self._interval_to_tss(block['intervals'][0])
            else:
                if 'repeats' in block:
                    repeats = block['repeats']
                else:
                    repeats = 1
                tss += sum([repeats*self._interval_to_tss(interval)
                            for interval in block['intervals']])
        return tss
