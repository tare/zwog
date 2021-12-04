<!-- markdownlint-disable -->

<a href="../zwog/utils.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `utils`
Routines for processing workouts. 



---

<a href="../zwog/utils.py#L9"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `WorkoutTransformer`
Class to process workout parse-trees. 




---

<a href="../zwog/utils.py#L49"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `block`

```python
block(b: list) → dict
```

Returns block. 

---

<a href="../zwog/utils.py#L11"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `duration`

```python
duration(d: list) → int
```

Returns duration in seconds. 

---

<a href="../zwog/utils.py#L22"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `durations`

```python
durations(d: list) → int
```

Returns total duration. 

---

<a href="../zwog/utils.py#L45"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `intervals`

```python
intervals(i: list) → Tuple[str, list]
```

Returns intervals. 

---

<a href="../zwog/utils.py#L34"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `power`

```python
power(p: list) → Union[float, list]
```

Returns power. 

---

<a href="../zwog/utils.py#L30"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `ramp`

```python
ramp(s: list) → dict
```

Returns ramp. 

---

<a href="../zwog/utils.py#L41"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `repeats`

```python
repeats(r: list) → Tuple[str, int]
```

Returns repeats. 

---

<a href="../zwog/utils.py#L26"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `steady_state`

```python
steady_state(s: list) → dict
```

Returns steady-state. 


---

<a href="../zwog/utils.py#L58"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ZWOG`
Zwift workout generator (ZWOG). 



**Args:**
 
 - <b>`workout`</b> (str):  Workout as a string. 
 - <b>`author`</b> (str):  Author. 
 - <b>`name`</b> (str):  Workout name. 
 - <b>`category`</b> (Optional[str]):  Workout category. 
 - <b>`subcategory`</b> (Optional[str]):  Workout subcategory. 

<a href="../zwog/utils.py#L69"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    workout: str,
    author: str = 'Zwift workout generator (https://github.com/tare/zwog)',
    name: str = 'Structured workout',
    category: Optional[str] = None,
    subcategory: Optional[str] = None
)
```






---

#### <kbd>property</kbd> json_workout





---

#### <kbd>property</kbd> tree_workout





---

#### <kbd>property</kbd> tss





---

#### <kbd>property</kbd> zwo_workout







---

<a href="../zwog/utils.py#L108"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `save_zwo`

```python
save_zwo(filename) → None
```

Saves the workout in the ZWO format. 



**Args:**
 
 - <b>`filename`</b>:  Filename. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
