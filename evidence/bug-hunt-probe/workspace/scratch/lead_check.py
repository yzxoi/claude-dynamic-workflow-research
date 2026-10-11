import sys; sys.path.insert(0,'.')
from inventory import Inventory
from pricing import quote
from scheduling import overlaps, earliest_slot, merge_overlaps
from metrics import percentile
i=Inventory({'a':5}); print('reserve all',i.reserve('a',5),i.available('a'))
print('quote at min',quote([{'unit_price_cents':1000,'quantity':1}]))
print('overlaps touching',overlaps((0,5),(5,10)))
print('slot before busy',earliest_slot([(5,10)],5,0,20))
print('percentile',percentile([1,2,3,4],50),percentile([1,2,3,4],100),percentile([5],100))
