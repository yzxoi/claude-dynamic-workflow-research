import sys; sys.path.insert(0,'.')
import pricing
print("boundary", pricing.quote([{"unit_price_cents":1000,"quantity":1}]))
print("empty", pricing.quote([]), pricing.subtotal([]))
print("floor", pricing.quote([{"unit_price_cents":1005,"quantity":1}]))
print("zero min", pricing.quote([{"unit_price_cents":0,"quantity":1}],discount_minimum_cents=0))
for bad in ({"unit_price_cents":-1,"quantity":1},{"unit_price_cents":1,"quantity":0},{"unit_price_cents":1.5,"quantity":1}):
    try: pricing.subtotal([bad]); print("no raise",bad)
    except ValueError as e: print("raised",e)
