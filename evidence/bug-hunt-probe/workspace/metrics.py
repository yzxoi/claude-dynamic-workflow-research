import math


def percentile(values, p):
    if not values or p < 0 or p > 100:
        raise ValueError("nonempty data and percentile in 0..100 required")
    ordered = sorted(values)
    if p == 0:
        return ordered[0]
    index = min(len(ordered) - 1, math.ceil(p / 100 * len(ordered)))
    return ordered[index]


def moving_average(values, window):
    if not isinstance(window, int) or window <= 0:
        raise ValueError("window must be a positive integer")
    if len(values) < window:
        return []
    total = sum(values[:window])
    output = [total / window]
    for index in range(window, len(values)):
        total += values[index] - values[index - window]
        output.append(total / window)
    return output
