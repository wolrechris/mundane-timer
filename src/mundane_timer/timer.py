import time, atexit, functools, os
import pandas as pd
from contextlib import contextmanager
from enum import Enum

class Timer:
    """
    A utility class for timing code execution across multiple labeled blocks.
    Results can be logged automatically, printed at program exit, or exported
    to CSV for later analysis.

    Features:
        - Context manager for timing arbitrary code blocks.
        - Optional contextual metadata stored alongside timing results.
        - Configurable logging behavior (none, results-only, or full).
        - Automatic results output at program exit when enabled.
    """

    class LogSetting(Enum):
        """
        Enum representing logging levels for timing results.

        Attributes:
            NONE: Disable all logging.
            RESULTS_ONLY: Log aggregated timing results at program exit.
            FULL: Log each timing result immediately as it is recorded.
            INHERIT: Inherit the logging behavior from the parent timer instance.
        """
        NONE = "none"
        RESULTS_ONLY = "results_only"
        FULL = "full"
        INHERIT = "inherit"

    def __init__(self, name, context_vars = None, log = LogSetting.RESULTS_ONLY):
        """
        Initialize a timer instance.

        Args:
            name (str): The name of the timer, used in printed and exported results.
            context_vars (list[tuple[str, Any]] | None): 
                Optional list of context variable pairs [(name, value), ...]
                to include with recorded results. Defaults to None.
            log (LogSetting): 
                Logging mode. Determines when timing results are printed.
                Defaults to LogSetting.RESULTS_ONLY.

        Raises:
            ValueError: If log is set to LogSetting.INHERIT without a parent context.
        """
        self.t = pd.DataFrame([])
        self.cv = pd.DataFrame([])
        self.name = name
        if context_vars == None:
            self.context_vars = []
        else:
            self.context_vars = context_vars
        self.log = log
        if log.value == "full" or log.value == "results_only":
            atexit.register(functools.partial(self.print_results))
        elif log.value == "inherit":
            raise ValueError("Cannot use log setting inherit as no previous log setting was specified!")


    @contextmanager
    def record(self, label, context_vars = [], log = LogSetting.INHERIT):
        """
        Context manager that measures and records the execution time of a code block.

        Usage:
            >>> t = Timer("Example")
            >>> with t.record("load_data"):
            ...     load_data_function()

        Args:
            label (str): Descriptive label for the timed code block.
            context_vars (list[tuple[str, Any]] | None): 
                Additional context variables for this specific block.
                These are merged with the timer’s global context variables.
                Defaults to None.
            log (LogSetting): 
                Logging level for this block. If INHERIT, uses the timer’s log setting.

        Yields:
            None: Used as a context manager for timing code execution.

        Notes:
            - Each timing result is stored in a pandas DataFrame.
            - When log=FULL, each timing result is printed immediately.
        """
        start = time.perf_counter()
        yield
        end = time.perf_counter()
        diff = end - start

        # Insert the diff value into the DataFrame
        if label not in self.t.columns:
            self.t[label] = pd.Series(dtype=float)
        nan_rows = self.t[self.t[label].isna()].index
        if len(nan_rows) > 0:
            self.t.at[nan_rows[0], label] = diff  # Fill the first NaN
        else:
            self.t.loc[len(self.t), label] = diff # Append a new row at the bottom

        # Log if set to full
        if log.value == "inherit": log = self.log
        if log.value == "full":
            print(f"--TIME-- {label} (#{len(self.t)-1}): {diff:.6f}s --TIME--")

        # Add the context vars
        if context_vars == None:
            context_vars_full = self.context_vars
        else:
            context_vars_full = self.context_vars + context_vars
        if len(context_vars_full) > 0:
            for var_pair in context_vars_full:
                self.cv.at[0, var_pair[0]] = var_pair[1] # Fill the first NaN

    def to_csv(self, output="/dev/stdout"):
        """
        Export timing results and context variables to a CSV file.

        Args:
            output (str): Path to the output CSV file. 
                Defaults to "/dev/stdout" for console output.

        Notes:
            - If the file exists, new results are appended.
            - Each row includes average and sum of timing values
              along with any stored context variables.
        """        # Read file or create empty dataframe
        if output == "/dev/stdout" or not os.path.exists(output):
            df = pd.DataFrame([])
        else:
            df = pd.read_csv(output)
        avgs = self.t.mean()
        avgs.index = [col + "_avg" for col in avgs.index]
        sums = self.t.sum()
        sums.index = [col + "_sum" for col in sums.index]
        new_vals = pd.concat([pd.DataFrame([{**avgs, **sums}]), self.cv.reset_index(drop=True)], axis=1)
        df = pd.concat([df, new_vals], axis=0) # add new values (1 row) to the bottom of existing df

        df.to_csv(output, index=False)


    def print_results(self, labels = None, max_entries_shown = 0):
        """
        Print a summary of all recorded timing results to stdout.

        Args:
            labels (list[str] | None): 
                Optional subset of labels to print. If None, print all.
            max_entries_shown (int): 
                Maximum number of entries to show per label. 
                If 0, show only summary statistics.

        Output:
            Prints the following for each label:
                - Run times (optionally truncated)
                - Number of runs
                - Average runtime
                - Total runtime
        """
        print(f'TIMER RESULTS OF {self.name}')
        for k, l in self.t.items():
            # Only labels that are either specified or if none are specified
            if (labels == None) or (k in labels):
                l = l.dropna(how='all')
                print('')
                print(f'    Timing results for {k}')
                print('    ------------------------------')
                if max_entries_shown != 0:
                    if len(l) <= max_entries_shown:
                        for index, run_result in enumerate(l):
                            print(f'     Run {index}:    {run_result:.6f}')
                    else:
                        start_range = (0, int(max_entries_shown/2))
                        end_range = (int(len(l) - 1 - (max_entries_shown/2 - 1)), len(l))
                        for index in range(start_range[0], start_range[1]):
                            print(f'     Run {index}:    {l[index]:.6f}')
                        print('     ...')
                        for index in range(end_range[0], end_range[1]):
                            print(f'     Run {index}:    {l[index]:.6f}')
                    print('    ------------------------------')
                print(f'    N:   {len(l)}')
                print(f'    AVG: {sum(l) / len(l):.6f}')
                print(f'    SUM: {sum(l):.6f}')
                print('')

