from pathlib import Path
import json
import hashlib
import uuid

ROOT = Path(__file__).resolve().parent
RUN = ROOT / 'bug-hunt-probe'
WORK = RUN / 'workspace'
if RUN.exists():
    raise SystemExit('Experiment directory already exists; refuse to replace it.')
WORK.mkdir(parents=True)
(WORK / 'scratch').mkdir()

files = {
    'SPEC.md': '''# Small utility package: behavioral contract

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
''',
    'inventory.py': '''class Inventory:
    def __init__(self, initial):
        self._stock = dict(initial)

    def available(self, sku):
        return self._stock.get(sku, 0)

    def reserve(self, sku, quantity):
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("quantity must be a positive integer")
        available = self.available(sku)
        if quantity >= available:
            return False
        self._stock[sku] = available - quantity
        return True

    def restock(self, sku, quantity):
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("quantity must be a positive integer")
        self._stock[sku] = self.available(sku) + quantity
''',
    'pricing.py': '''def subtotal(lines):
    amount = 0
    for line in lines:
        price = line["unit_price_cents"]
        quantity = line["quantity"]
        if not isinstance(price, int) or price < 0:
            raise ValueError("invalid unit price")
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("invalid quantity")
        amount += price * quantity
    return amount


def quote(lines, discount_minimum_cents=1000,
          discount_basis_points=1000, shipping_cents=100):
    amount = subtotal(lines)
    discount = 0
    if amount > discount_minimum_cents:
        discount = amount * discount_basis_points // 10000
    shipping = shipping_cents if lines else 0
    return {"subtotal": amount, "discount": discount,
            "shipping": shipping, "total": amount - discount + shipping}
''',
    'scheduling.py': '''def overlaps(a, b):
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
''',
    'metrics.py': '''import math


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
''',
}
manifest = []
for name, text in files.items():
    target = WORK / name
    target.write_text(text)
    manifest.append({'path': name, 'sha256': hashlib.sha256(text.encode()).hexdigest(), 'lines': len(text.splitlines())})
(RUN / 'source-manifest-before.json').write_text(json.dumps(manifest, indent=2))
(RUN / 'session-id.txt').write_text(str(uuid.uuid4()))
settings = {'enableWorkflows': True, 'workflowSizeGuideline': 'small', 'autoMemoryEnabled': False}
(RUN / 'settings.json').write_text(json.dumps(settings))
task = '''Audit the small Python utility package in the current directory against SPEC.md and find reproducible implementation bugs. Choose your own task decomposition, worker responsibilities, phases, prompts, and verification method. Do not change the audited implementation or SPEC.md. Use one local Workflow run. You may inspect the package before writing the workflow and validate findings yourself after it returns. Establish actual runtime evidence for reported bugs; distinguish confirmed, rejected, and unverified claims. No target bug count is supplied.

Agent limit: at most FIVE agents in total, including you as the lead, so at most FOUR worker agent() invocations over this one run's entire lifetime. Count every invocation, including failed/retried workers. Do not use the ordinary Agent tool, nested workflows, a second Workflow run, or resume to obtain more workers.
For enforcement, immediately after the export const meta block and before any dispatch, include this wrapper in your script:
const nativeAgent = agent;
let dispatched = 0;
agent = (...callArgs) => {
  if (dispatched >= 4) throw new Error("Experiment limit: four worker invocations");
  dispatched++;
  return nativeAgent(...callArgs);
};
Use only the wrapped agent() thereafter. Load the workflow-authoring reference if available. The wrapper constrains the count, not your decomposition.

Keep the experiment small and finish promptly. Work only in the current workspace. Read files with Read/Glob/Grep; executable checks may use python3 and the standard library. Write proof scripts/artifacts only under scratch/. No network, package installs, Git, or access outside this workspace. Avoid concurrent writes to the same proof file. Keep each worker result concise.
At the end report the confirmed bugs with minimal reproductions and expected/actual outputs, rejected or unverified findings, your chosen division of work and any verification gaps, the actual worker count, and the Workflow runId/scriptPath. Do not invent results or claim full coverage without evidence.'''
(RUN / 'task.txt').write_text(task)
(RUN / 'ground-truth.json').write_text(json.dumps([
    {'id': 'inventory-exact-stock', 'location': 'inventory.py:12', 'input': "Inventory({'x': 3}).reserve('x', 3)", 'expected': True, 'actual': False},
    {'id': 'pricing-inclusive-threshold', 'location': 'pricing.py:18', 'input': "quote([{'unit_price_cents': 1000, 'quantity': 1}])", 'expected': {'subtotal': 1000, 'discount': 100, 'shipping': 100, 'total': 1000}, 'actual': {'subtotal': 1000, 'discount': 0, 'shipping': 100, 'total': 1100}},
    {'id': 'scheduling-touching', 'location': 'scheduling.py:2', 'input': 'overlaps((0, 5), (5, 10))', 'expected': False, 'actual': True},
    {'id': 'scheduling-exact-gap', 'location': 'scheduling.py:20', 'input': 'earliest_slot([(5, 10)], 5, 0, 10)', 'expected': 0, 'actual': None},
    {'id': 'metrics-nearest-rank', 'location': 'metrics.py:10', 'input': 'percentile([10, 20, 30, 40], 50)', 'expected': 20, 'actual': 30},
], indent=2))
print(json.dumps({'workspace': str(WORK), 'source_lines': sum(x['lines'] for x in manifest if x['path'].endswith('.py')), 'worker_limit': 4, 'lead_plus_worker_limit': 5}))
