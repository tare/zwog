<!-- markdownlint-disable -->

<a href="../zwog/utils.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `utils`
Routines for processing workouts. 



---

<a href="../zwog/utils.py#L10"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `WorkoutTransformer`
Class to process workout parse-trees. 




---

<a href="../zwog/utils.py#L54"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `block`

```python
block(b: list) → dict
```

Return block. 

---

<a href="../zwog/utils.py#L13"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `duration`

```python
duration(d: list) → int
```

Return duration in seconds. 

---

<a href="../zwog/utils.py#L27"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `durations`

```python
durations(d: list) → int
```

Return total duration. 

---

<a href="../zwog/utils.py#L50"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `intervals`

```python
intervals(i: list) → Tuple[str, list]
```

Return intervals. 

---

<a href="../zwog/utils.py#L39"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `power`

```python
power(p: list) → Union[float, list]
```

Return power. 

---

<a href="../zwog/utils.py#L35"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `ramp`

```python
ramp(s: list) → dict
```

Return ramp. 

---

<a href="../zwog/utils.py#L46"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `repeats`

```python
repeats(r: list) → Tuple[str, int]
```

Return repeats. 

---

<a href="../zwog/utils.py#L31"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `steady_state`

```python
steady_state(s: list) → dict
```

Return steady-state. 


---

<a href="../zwog/utils.py#L64"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ZWOG`
Zwift workout generator (ZWOG). 

<a href="../zwog/utils.py#L67"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

Initialize ZWOG. 



**Args:**
 
 - <b>`workout`</b>:  Workout as a string. 
 - <b>`author`</b>:  Author. 
 - <b>`name`</b>:  Workout name. 
 - <b>`category`</b>:  Workout category. 
 - <b>`subcategory`</b>:  Workout subcategory. 


---

#### <kbd>property</kbd> json_workout

Return workout as JSON. 

---

#### <kbd>property</kbd> tss

Get TSS. 

---

#### <kbd>property</kbd> zwo_workout

Get the workout as ZWO. 



---

<a href="../zwog/utils.py#L115"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `save_zwo`

```python
save_zwo(filename) → None
```

Save the workout in the ZWO format. 



**Args:**
 
 - <b>`filename`</b>:  Filename. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
