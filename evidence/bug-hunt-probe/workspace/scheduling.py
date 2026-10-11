def overlaps(a, b):
    return a[0] <= b[1] and b[0] <= a[1]


def merge_overlaps(intervals):
    merged = []
    for start, end in sorted(intervals):
        if merged and start < merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def earliest_slot(busy, duration, earliest, latest):
    start = earliest
    for begin, end in merge_overlaps(busy):
        if end <= start:
            continue
        if start + duration < begin:
            return start if start + duration <= latest else None
        start = max(start, end)
        if start + duration > latest:
            return None
    return start if start + duration <= latest else None
