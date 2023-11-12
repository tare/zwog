"""constants.py."""

ZWOG_GRAMMAR = r"""workout: block*
block: [repeats "x"] intervals
intervals: interval~1 ("," interval)*
interval: ramp|steady_state
steady_state: durations "@" steady_state_power "%" "FTP"
ramp: durations "from" ramp_power "%" "FTP"
durations: duration+
duration: NUMBER TIME_UNIT
time_unit: TIME_UNIT
TIME_UNIT: "sec"|"s"|"min"|"m"|"hrs"|"h"
repeats: INT
steady_state_power: NUMBER -> power
ramp_power: NUMBER "to" NUMBER -> power

%ignore WS
%import common.WS
%import common.INT
%import common.NUMBER
"""

SECONDS_IN_HOUR = 3600
SECONDS_IN_MINUTE = 60

INTERVALST_LENGTH = 2
