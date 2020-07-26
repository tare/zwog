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

You can use the command line application
```bash
$ zwog --help
usage: zwog [-h] -i INPUT_FILE [-o OUTPUT_FILE] [-v]

Zwift workout generator

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_FILE, --input_file INPUT_FILE
                        input filename
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        output filename
  -v, --version         show program's version number and exit
```
or call it from Python
```python
import zwog

workout_text = '15min from 10 to 50% FTP 5min from 50 to 70% FTP 2x 0.5hrs @ 100% FTP, 0.5hrs @ 50% FTP, 10min from 80 to 90% FTP 2min @ 50% FTP\n2min @ 50% FTP\n 10min @ 50% FTP, 10min @ 60% FTP 10min from 50 to 10% FTP'
workout = zwog.ZWOG(workout_text)
workout.save_zwo('workout.xml')
print(workout)
print('%d TSS'%(round(workout.tss)))
```
