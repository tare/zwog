# Zwift workout generator

Have you ever been frustrated by any WYSIWYG workout editor, such as the [Zwift Workout editor](https://zwift.com/news/12975-zwift-how-to-creating-a-custom-workout) and the [TrainingPeaks Workout Builder](https://help.trainingpeaks.com/hc/en-us/articles/235164967-Structured-Workout-Builder)?

ZWOG makes it easier to generate structured workouts using a syntax similar to the one used on [What's on Zwift?](https://whatsonzwift.com).

### Syntax

The basic building blocks are ramp intervals
```
10min from 30 to 60% FTP
```
and steady state intervals
```
2hrs @ 60% FTP
```
Interval durations can be given either in seconds (`sec`,`s`), minutes (`min`,`m`), or hours (`hrs`,`h`).

Moreover, it is possible to create repeated intervals  
```
4x 5min @ 95% FTP, 5min @ 85% FTP
```

Finally, a complete workout can be defined as follows
```
10min from 40 to 85% FTP
3x 5min @ 95% FTP, 5min @ 86% FTP
5min @ 50% FTP
3x 5min @ 95% FTP, 5min @ 86% FTP
10min from 75 to 55% FTP
```

### Usage

```python
from zwog import ZWOG

workout_text = '15min from 10 to 50% FTP 5min from 50 to 70% FTP 2x 0.5hrs @ 100% FTP, 0.5hrs @ 50% FTP, 10min from 80 to 90% FTP 2min @ 50% FTP\n2min @ 50% FTP\n 10min @ 50% FTP, 10min @ 60% FTP 10min from 50 to 10% FTP'
workout = ZWOG(workout_text)
workout.save_zwo('workout.xml')
print(workout)
print('%d TSS'%(round(zwog.tss)))
```
