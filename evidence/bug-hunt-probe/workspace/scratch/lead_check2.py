import sys; sys.path.insert(0,'.')
from metrics import percentile, moving_average
from scheduling import earliest_slot
d=list(range(1,11)); print(percentile(d,50),percentile(d,10),percentile(d,70))
print(earliest_slot([(5,10)],5,0,20), earliest_slot([(0,2),(4,10)],2,0,20))
print(moving_average([1e16,1,1,1,1e16],2), moving_average([1,2,3,4],2))
