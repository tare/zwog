from lark import Lark
from lark import Transformer
from xml.etree.ElementTree import (ElementTree, Element,
                                   SubElement, tostring)

class TreeToJson(Transformer):
    def duration(self,d):
        if d[1] == 'hrs' or d[1] == 'h':
            return int(d[0]*3600)
        elif d[1] == 'min' or d[1] == 'm':
            return int(d[0]*60)
        else:
            return int(d[0])
    def durations(self,d):
        return sum(d)
    def steady_state(self,s):
        return dict(duration=s[0],power=s[1])
    def ramp(self,s):
        return dict(duration=s[0],power=s[1])
    def power(self,p):
        if len(p) == 1:
            return p[0]
        else:
            return p
    def repeats(self,r):
        return 'repeats',r[0]
    def intervals(self,i):
        return 'intervals',i
    def block(self,b):
        return dict(b)
    INT = int
    NUMBER = float
    TIME_UNIT = str
    workout = list

class ZWOG():
    def __init__(self,workout,author=('Zwift workout generator '
                                      '(https://github.com/tare/zwog)'),
                 name='Structured workout',
                 category=None,subcategory=None):

        parser = Lark(r"""
            workout: block*
            block: [repeats "x"] intervals
            intervals: (ramp|steady_state ("," (steady_state|ramp))*)
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
        """,start='workout')

        self.__name = name
        self.__author = author
        self.__category = category
        self.__subcategory = subcategory

        self.__tree_workout = parser.parse(workout)
        self.__json_workout = TreeToJson().transform(parser.parse(workout))
        self.__pretty_workout = self._json_to_pretty(self.__json_workout)
        self.__zwo_workout = self._json_to_zwo(self.__json_workout)
        self.__tss = self._json_to_tss(self.__json_workout)

    def save_zwo(self,filename):
        self.__zwo_workout.write(filename)

    def __str__(self):
        return self.__pretty_workout

    @property
    def tss(self):
        return self.__tss

    @property
    def json_workout(self):
        return self.__json_workout

    @property
    def tree_workout(self):
        return self.__tree_workout.pretty()

    @property
    def zwo_workout(self):
        return tostring(self.__zwo_workout.getroot(),encoding='unicode')

    def _is_ramp(self,x):
        return bool(len(x['intervals']) == 1 and
            isinstance(x['intervals'][0]['power'],list))

    def _is_steady_state(self,x):
        return bool(len(x['intervals']) == 1 and not
            isinstance(x['intervals'][0]['power'],list))

    def _is_intervalst(self,x):
        return bool(len(x['intervals']) == 2 and not
            isinstance(x['intervals'][0]['power'],list) and not
            isinstance(x['intervals'][1]['power'],list))

    def _interval_to_xml(self,interval,repeats=1):
        if not isinstance(interval,list):
            if not isinstance(interval['power'],list):
                element = Element('SteadyState')
                element.set('Duration',str(interval['duration']))
                element.set('Power',str(interval['power']/100))
            else:
                element = Element('Ramp')
                element.set('Duration',str(interval['duration']))
                element.set('PowerLow',str(interval['power'][0]/100))
                element.set('PowerHigh',str(interval['power'][1]/100))
        else:
            element = Element('IntervalsT')
            element.set('Repeat',str(repeats))
            element.set('OnDuration',str(interval[0]['duration']))
            element.set('OnPower',str(interval[0]['power']/100))
            element.set('OffDuration',str(interval[1]['duration']))
            element.set('OffPower',str(interval[1]['power']/100))

        return element

    def _json_to_zwo(self,x):
        root = Element('workout_file')

        for child,value in [('author',self.__author),
                            ('name',self.__name),
                            ('description','%s\n\n%s'%(
                                ('This workout was generated '
                                 'using ZWOG.'),self._json_to_pretty(x))),
                            ('sportType','bike')]:
            tmp = SubElement(root,child)
            tmp.text = value

        if self.__category is not None:
            tmp = SubElement(root,'category')
            tmp.text = self.__category

        if self.__subcategory is not None:
            tmp = SubElement(root,'subcategory')
            tmp.text = self.__subcategory

        tmp = SubElement(root, 'workout')
        for block_idx,block in enumerate(x):
            # warmup and ramp
            if ((block_idx == 0 or block_idx == (len(x)-1)) and
                self._is_ramp(block)):
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
                    if self._is_intervalst(block): # intervalst
                        tmp.append(self._interval_to_xml(block['intervals'],
                                                         repeats=repeats))
                    else: # non intervalst
                        for _ in range(repeats):
                            for interval in block['intervals']:
                                tmp.append(self._interval_to_xml(interval))
        tree = ElementTree(root)
        return tree

    def _duration_to_pretty_str(self,duration):
        pretty_str = ''
        if int(duration/3600) > 0:
            pretty_str += '%dh'%(int(duration/3600))
        if int((duration % 3600)/60) > 0:
            pretty_str += '%dm'%(int((duration % 3600)/60))
        if duration % 60 > 0:
            pretty_str += '%ds'%(int((duration % 60)))
        return pretty_str

    def _interval_to_str(self,interval):
        if isinstance(interval['power'],list):
            return '%s from %.0f to %.0f%% FTP'%(
                self._duration_to_pretty_str(interval['duration']),
                interval['power'][0],interval['power'][1])
        else:
            return '%s @ %.0f%% FTP'%(
                self._duration_to_pretty_str(interval['duration']),
                interval['power'])

    def _interval_to_tss(self,interval):
        if isinstance(interval['power'],list):
            min_power = min([interval['power'][0],interval['power'][1]])
            max_power = max([interval['power'][0],interval['power'][1]])
            tss = interval['duration']/3600*min_power
            tss += interval['duration']/3600*(max_power-min_power)/2
            return tss
        else:
            tss = interval['duration']/3600*interval['power']
        return tss

    def _json_to_pretty(self,x):
        output = []
        for block in x:
            # ramp or steady state
            if self._is_ramp(block) or self._is_steady_state(block) :
                output.append(self._interval_to_str(block['intervals'][0]))
            else:
                if 'repeats' in block:
                    tmp = '%dx '%(block['repeats'])
                else:
                    tmp = '1x '
                output.append(tmp +', '.join([
                    self._interval_to_str(interval)
                    for interval in block['intervals']]))
        return '\n'.join(output)

    def _json_to_tss(self,x):
        tss = 0
        for block in x:
            # ramp or steady state
            if self._is_ramp(block) or self._is_steady_state(block) :
                tss += self._interval_to_tss(block['intervals'][0])
            else:
                if 'repeats' in block:
                    repeats = block['repeats']
                else:
                    repeats = 1
                tss += sum([repeats*self._interval_to_tss(interval)
                            for interval in block['intervals']])
        return tss
