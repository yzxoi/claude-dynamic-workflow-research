# Small utility package: behavioral contract

The four Python modules use only the standard library. Audit them against the contracts below. Inputs outside these contracts need not be supported unless a function explicitly validates them.

## inventory.py

`Inventory(initial)` starts from a mapping of SKU strings to nonnegative integer quantities. `available(sku)` returns the remaining quantity, or zero for an unknown SKU.

`reserve(sku, quantity)` accepts strictly positive integer quantities. It returns `True` and reduces availability by exactly `quantity` if enough units remain, including when the request consumes all remaining units. Otherwise it returns `False` without changing state. Invalid quantities raise `ValueError` without changing state.

`restock(sku, quantity)` adds a strictly positive integer quantity, creating an unknown SKU if needed. Invalid quantities raise `ValueError` without changing state.

## pricing.py

`subtotal(lines)` sums `unit_price_cents * quantity` for lines with nonnegative integer prices and strictly positive integer quantities. Empty input returns zero; invalid lines raise `ValueError`.

`quote(lines, discount_minimum_cents=1000, discount_basis_points=1000, shipping_cents=100)` applies a discount when the subtotal is **at least** the minimum. The discount is `floor(subtotal * basis_points / 10000)` and applies only to merchandise. Shipping is then added. Empty input has no shipping charge. Threshold and shipping are nonnegative integers; basis points is an integer in 0..10000. The result has `subtotal`, `discount`, `shipping`, and `total`, all integer cents.

## scheduling.py

Intervals are valid `(start, end)` integer pairs with `start < end`, interpreted as half-open `[start, end)`. Intervals that merely touch do not overlap.

`overlaps(a, b)` returns whether the intervals share positive-length time.

`merge_overlaps(intervals)` sorts and merges overlapping intervals. Touching intervals remain separate. Empty input returns an empty list. It must not mutate the input list.

`earliest_slot(busy, duration, earliest, latest)` returns the earliest integer start `s` for which `[s, s + duration)` is inside `[earliest, latest)` and overlaps none of `busy`. A slot ending exactly at `latest` or exactly at a busy interval's start is valid. `duration` is a strictly positive integer. Busy intervals are valid but can be unordered, overlap, or lie outside the search window. Return `None` if no slot fits. Do not mutate `busy`.

## metrics.py

`percentile(values, p)` returns the nearest-rank percentile without mutating `values`. For nonempty integer data and `0 < p <= 100`, rank is `ceil(p / 100 * n)` (one-based), and the result is the value at that rank in sorted data. At `p == 0`, return the minimum. Reject empty data or `p` outside 0..100 with `ValueError`.

`moving_average(values, window)` returns one arithmetic mean per complete consecutive window, in order. `window` is a strictly positive integer. Fewer values than the window returns an empty list. Do not mutate `values`.
