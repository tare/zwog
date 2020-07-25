from lark import Lark
from lark import Transformer
from xml.etree.ElementTree import ElementTree, Element, SubElement, tostring

class TreeToJson(Transformer):
  def duration(self,d):
    if d[1] == 'hrs' or d[1] == 'h':
      return int(d[0]*3600)
    elif d[1] == 'min' or d[1] == 'm':
      return int(d[0]*60)
    else:
      return int(d[0])
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
    return "repeats",r[0]
  def intervals(self,i):
    return "intervals",i
  def block(self,b):
    return {y:x for y,x in b}
  INT = int
  NUMBER = float
  TIME_UNIT = str
  workout = list

class ZWOG():
  def __init__(self,workout):

    parser = Lark(r"""
      workout: block*
      block: [repeats "x"] intervals
      intervals: (ramp|steady_state ("," (steady_state|ramp))*)
      steady_state: duration "@" steady_state_power "%" "FTP"
      ramp: duration "from" ramp_power "%" "FTP"
      duration: NUMBER TIME_UNIT
      time_unit: TIME_UNIT
      TIME_UNIT: ("sec"|"s"|"min"|"hrs"|"h")
      repeats: INT
      steady_state_power: NUMBER -> power 
      ramp_power: NUMBER "to" NUMBER -> power
    
      %ignore WS
      %import common.WS
      %import common.INT
      %import common.NUMBER
    """,start='workout')

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
    if len(x['intervals']) == 1 and isinstance(x['intervals'][0]['power'],list):
      return True
    else:
      return False
  
  def _is_steady_state(self,x):
    if len(x['intervals']) == 1 and not isinstance(x['intervals'][0]['power'],list):
      return True
    else:
      return False
  
  def _is_intervalst(self,x):
    if len(x['intervals']) == 2 and not isinstance(x['intervals'][0]['power'],list) and not isinstance(x['intervals'][1]['power'],list):
      return True
    else:
      return False
  
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
  
  def _json_to_zwo(self,x,name='Structured workout',author='ZWOG (https://github.com/tare/ZWOG)'):
    root = Element('workout_file')
  
    for child,value in [('author',author),('name',name),('description','%s\n\n%s'%('This workout was generated using ZWOG.',self._json_to_pretty(x))),('sportType','bike')]:
      tmp = SubElement(root,child)
      tmp.text = value
  
    tmp = SubElement(root, 'workout')
    for block_idx,block in enumerate(x):
      if (block_idx == 0 or block_idx == (len(x)-1)) and self._is_ramp(block): # warmup and ramp
        element = self._interval_to_xml(block['intervals'][0])
        if block_idx == 0:
          element.tag = 'Warmup'
        else:
          element.tag = 'Cooldown'
        tmp.append(element)
      else:
        if self._is_ramp(block) or self._is_steady_state(block): # ramp or steady state
          tmp.append(self._interval_to_xml(block['intervals'][0]))
        else:
          if 'repeats' in block:
            repeats = block['repeats']
          else:
            repeats = 1
          if self._is_intervalst(block): # intervalst
            tmp.append(self._interval_to_xml(block['intervals'],repeats=repeats))
          else: #  non intervalst
            for _ in range(repeats):
              for interval in block['intervals']:
                tmp.append(self._interval_to_xml(interval))
  
    tree = ElementTree()
    tree._setroot(root)
    return tree
  
  def _interval_to_str(self,interval):
    if isinstance(interval['power'],list):
      return '%dsec from %.0f to %.0f%% FTP'%(interval['duration'],
                                              interval['power'][0],
                                              interval['power'][1])
    else:
      return '%dsec @ %.0f FTP'%(interval['duration'],
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
    for block_idx,block in enumerate(x):
      if self._is_ramp(block) or self._is_steady_state(block) : # ramp or steady state
        output.append(self._interval_to_str(block['intervals'][0]))
      else:
        if 'repeats' in block:
          tmp = '%dx '%(block['repeats'])
        else:
          tmp = '1x '
        output.append(tmp + ', '.join([self._interval_to_str(interval) for interval in block['intervals']]))
  
    return '\n'.join(output)
  
  def _json_to_tss(self,x):
    tss = 0
    for block_idx,block in enumerate(x):
      if self._is_ramp(block) or self._is_steady_state(block) : # ramp or steady state
        tss += self._interval_to_tss(block['intervals'][0])
      else:
        if 'repeats' in block:
          repeats = block['repeats']
        else:
          repeats = 1
        tss += sum([repeats*self._interval_to_tss(interval) for interval in block['intervals']])
  
    return tss
