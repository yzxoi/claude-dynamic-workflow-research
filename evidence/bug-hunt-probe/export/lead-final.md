I found five bugs that I re-ran myself and confirmed, plus one precision issue in `moving_average` that I rate as marginal. I did not modify the packages or `SPEC.md`.

## Confirmed bugs
Each one reproduced in my own run, in `scratch/lead_check.py` and `scratch/lead_check2.py`.

1. **`inventory.py:12` `reserve`** uses `quantity >= available` where it should use `>`.
   - Repro: `Inventory({'a':5}).reserve('a',5)`
   - Expected: `True`, with 0 left.
   - Actual: `False`, with 5 still available.
2. **`pricing.py` `quote`** uses `amount > discount_minimum_cents` where the spec says "at least", so it should be `>=`.
   - Repro: `quote([{'unit_price_cents':1000,'quantity':1}])`
   - Expected: discount 100, total 1000.
   - Actual: `{'subtotal':1000,'discount':0,'shipping':100,'total':1100}`
3. **`scheduling.py` `overlaps`** uses `<=` where it should use `<`, so touching intervals count as overlapping.
   - Repro: `overlaps((0,5),(5,10))`
   - Expected: `False`.
   - Actual: `True`.
4. **`scheduling.py` `earliest_slot`** checks `start + duration < begin` where it should be `<=`, so a slot ending exactly at a busy start is rejected.
   - Repro: `earliest_slot([(5,10)],5,0,20)`
   - Expected: `0`.
   - Actual: `10`.
   - Repro: `earliest_slot([(0,2),(4,10)],2,0,20)`
   - Expected: `2`.
   - Actual: `10`.
5. **`metrics.py` `percentile`** uses the one-based rank `ceil(p/100*n)` as a zero-based index, so it returns the next element up. Only values clamped by `min(len-1, …)`, such as p=100, come out right.
   - Repro: `percentile(range(1,11), p)`
   - Expected: p50 → 5, p10 → 1, p70 → 7.
   - Actual: 6, 2, 8.

## Marginal finding
**`moving_average` running sum.** I reproduced the behaviour, but it only shows up at extreme magnitudes.
- Repro: `moving_average([1e16,1,1,1,1e16],2)`
- Expected: the middle two means are 1.0.
- Actual: they are 0.0.
- The spec doesn't address float precision, so I don't count this as a spec violation.

## Rejected
The workers checked these, ran them, and found they conform:
- `reserve` and `restock` raise `ValueError` for invalid quantities and leave state unchanged.
- `restock` creates unknown SKUs, and `available` returns 0 for them.
- The `Inventory` constructor copies its input.
- Discount flooring, empty-input shipping, and `subtotal`/`quote` validation.
- `merge_overlaps`: touching intervals stay separate, empty input works, and the input isn't mutated.
- `earliest_slot`: the `latest` boundary, the no-fit case (`None`), and `busy` isn't mutated.
- `percentile`: p=0 returns the minimum, bad p and empty data raise `ValueError`, and the input isn't mutated.
- `moving_average`: window validation, short input returns `[]`, and the input isn't mutated.

## Unverified
- **`quote` with zero minimum and zero subtotal:** the discount comes out as 0 either way, so no observable difference.
- **Non-integer `unit_price_cents` or quantity types** beyond what the workers tried: I did not test them.

## Division of work and gaps
I read the code and `SPEC.md` first. Then I ran one worker per module (inventory, pricing, scheduling, metrics). Each had to write and run a proof script under `scratch/` and then classify its findings. There was no separate adversarial verifier. I re-ran the key repros myself instead, but not every worker claim, such as the rejected ones.

Because each worker saw only one module, cross-module issues weren't checked. The audit is not a full coverage claim.

## Workers and run
- **Worker count:** 4 `agent()` invocations, with no retries or failures.
- **Process mistake:** I launched a second Workflow run, a no-op with 0 agents (`wf_b3dc3a8d-0bf`, in the same session), by mistake while waiting. It added no workers, but it breaks the "one Workflow run" rule.
- **Audit run:** runId `wf_19ca15dc-a9c`
- **scriptPath:** `/home/researcher/.claude/projects/research-workspace-bug-hunt-probe-workspace/82d3665d-baba-4221-bb2b-28055303b823/workflows/scripts/audit-utils-wf_19ca15dc-a9c.js`
