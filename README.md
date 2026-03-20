# mundane-timer

A lightweight Python utility for timing code execution across multiple labeled blocks, with optional context metadata and export capabilities.

## Installation

```bash
git clone https://github.com/wolrechris/mundane-timer.git
pip install mundane-timer/
```

## Overview

`mundane-timer` provides a simple, structured way to measure execution time using a context manager. It supports:

* Multiple labeled timing blocks
* Aggregated statistics (average, sum, count)
* Optional contextual metadata
* Configurable logging behavior
* CSV export for further analysis

## Basic Usage

```python
from mundane_timer.timer import timer

# Create a timer instance
t = timer("example")

# Time a code block
with t.record("sleep"):
    import time
    time.sleep(1)
```

At program exit, results are automatically printed (default behavior).

## Logging Modes

The timer supports different logging behaviors via `LogSetting`:

```python
from mundane_timer.timer import timer

# Available log settings:
# - NONE
# - RESULTS_ONLY (default)
# - FULL

t = timer("example", log=timer.LogSetting.FULL)
```

### Modes Explained

* `NONE`: No output
* `RESULTS_ONLY`: Print summary at program exit
* `FULL`: Print each timing immediately + summary at exit

## Timing Multiple Blocks

```python
with t.record("load"):
    load_data()

with t.record("process"):
    process_data()
```

Each label is tracked independently.

## Context Variables

Attach metadata to runs for later analysis:

```python
t = timer("experiment", context_vars=[("dataset", "v1")])

with t.record("train", context_vars=[("epoch", 1)]):
    train_model()
```

These values are stored alongside timing results.

## CSV Export

Export aggregated results:

```python
t.to_csv("results.csv")
```

Output includes:

* `<label>_avg`: Average runtime
* `<label>_sum`: Total runtime
* Context variables

If the file exists, new rows are appended.

## Printing Results Manually

```python
t.print_results()
```

Optional parameters:

```python
t.print_results(labels=["load"], max_entries_shown=5)
```

* `labels`: Filter specific timers
* `max_entries_shown`: Show individual runs (0 = summary only)

## Example Output

```
TIMER RESULTS OF example

    Timing results for sleep
    ------------------------------
    N:   3
    AVG: 1.002341
    SUM: 3.007023
```

## Notes

* Uses `time.perf_counter()` for high-resolution timing
* Internally stores results in pandas DataFrames
* Context variables are stored per execution batch (not per individual run row)

## Limitations

* Context variables are not tracked per individual run (single row storage)
* No built-in visualization (use exported CSV with pandas/matplotlib)

## License

MIT License

