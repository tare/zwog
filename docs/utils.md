<!-- markdownlint-disable -->

<a href="../src/zwog/utils.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `utils`
Routines for processing workouts.

**Global Variables**
---------------
- **INTERVALST_LENGTH**
- **SECONDS_IN_HOUR**
- **SECONDS_IN_MINUTE**
- **ZWOG_GRAMMAR**

---

<a href="../src/zwog/utils.py#L433"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `main`

```python
main() → NoReturn
```

ZWOG command line interface.


---

<a href="../src/zwog/utils.py#L19"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Interval`
Interval data.

<a href="../<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(duration: int, power: Union[float, List[float]]) → None
```









---

<a href="../src/zwog/utils.py#L27"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Block`
Block data.

<a href="../<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(intervals: List[Interval], repeats: int = 1) → None
```









---

<a href="../src/zwog/utils.py#L35"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `WorkoutTransformer`
Class to process workout parse-trees.




---

<a href="../src/zwog/utils.py#L99"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `block`

```python
block(b: List[Tuple[str, Union[int, List[Interval]]]]) → Block
```

Return block.

---

<a href="../src/zwog/utils.py#L46"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `durations`

```python
durations(d: List[Tuple[Union[int, float], str]]) → int
```

Return total duration.

---

<a href="../src/zwog/utils.py#L71"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `interval`

```python
interval(s: List[Tuple[int, Union[float, List[float]]]]) → Interval
```

Return steady-state.

---

<a href="../src/zwog/utils.py#L94"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `intervals`

```python
intervals(i: List[Interval]) → Tuple[str, List[Interval]]
```

Return intervals.

---

<a href="../src/zwog/utils.py#L76"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `power`

```python
power(p: List[float]) → Union[float, List[float]]
```

Return power.

---

<a href="../src/zwog/utils.py#L86"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `repeats`

```python
repeats(r: List[int]) → Tuple[str, int]
```

Return repeats.


---

<a href="../src/zwog/utils.py#L107"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ZWOG`
Zwift workout generator (ZWOG).

<a href="../src/zwog/utils.py#L110"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    workout: str,
    author: str = 'Zwift workout generator (https://github.com/tare/zwog)',
    name: str = 'Structured workout',
    category: Optional[str] = None,
    subcategory: Optional[str] = None
) → None
```

Initialize ZWOG.



**Args:**

 - <b>`workout`</b>:  Workout as a string.
 - <b>`author`</b>:  Author.
 - <b>`name`</b>:  Workout name.
 - <b>`category`</b>:  Workout category.
 - <b>`subcategory`</b>:  Workout subcategory.


---

#### <kbd>property</kbd> element_workout

Get the workout as element.

---

#### <kbd>property</kbd> tss

Get TSS.

---

#### <kbd>property</kbd> workout

Return workout.

---

#### <kbd>property</kbd> zwo_workout

Get the workout as ZWO.



---

<a href="../src/zwog/utils.py#L142"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `save_zwo`

```python
save_zwo(filename: str) → None
```

Save the workout in the ZWO format.



**Args:**

 - <b>`filename`</b>:  Filename.




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
