import sys; sys.path.insert(0,'.')
import scheduling as s
print('overlaps touching', s.overlaps((0,5),(5,10)))
b=[(5,10),(0,2)]; print('merge touching', s.merge_overlaps([(0,5),(5,10)]), 'merge overlap', s.merge_overlaps([(0,6),(5,10)]))
l=[(5,10),(0,2)]; s.merge_overlaps(l); print('mutation', l)
bb=[(5,10),(0,2)]
print('slot ends at busy start', s.earliest_slot([(5,10)],5,0,20), 'expected 0')
print('slot ends at latest', s.earliest_slot([],5,0,5), 'expected 0')
print('gap exact', s.earliest_slot([(0,2),(4,10)],2,0,20), 'expected 2')
print('unordered', s.earliest_slot(bb,3,0,20), 'expected 2', bb)
print('none', s.earliest_slot([(0,10)],5,0,12), 'expected None')
