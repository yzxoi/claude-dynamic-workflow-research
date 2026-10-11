import sys; sys.path.insert(0,'.')
from inventory import Inventory
i=Inventory({'a':5}); print('exact',i.reserve('a',5),i.available('a'))
i=Inventory({'a':5}); print('less',i.reserve('a',4),i.available('a'))
i=Inventory({'a':5}); print('more',i.reserve('a',6),i.available('a'))
for q in (0,-1,1.5,'1'):
    i=Inventory({'a':5})
    try: i.reserve('a',q)
    except ValueError: print('badres',q,i._stock)
    try: i.restock('a',q)
    except ValueError: print('badrest',q,i._stock)
i=Inventory({}); i.restock('n',3); print('new',i.available('n'),i.available('zz'))
d={'a':1}; j=Inventory(d); j.restock('a',1); print('mut',d)
