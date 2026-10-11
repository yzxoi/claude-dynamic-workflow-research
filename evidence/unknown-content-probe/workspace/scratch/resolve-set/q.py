import sys, doctest
sys.path.insert(0, '/research/claude-workflow-research/unknown-content-probe/workspace')
import jsonpointer
print(doctest.testmod(jsonpointer))
print(doctest.testfile('/research/claude-workflow-research/unknown-content-probe/workspace/doc/tutorial.rst', module_relative=False))
from jsonpointer import *
import collections
# from_parts round trip with odd parts
for parts in [['a/b','~','~1','~0',''],[0,1],['']]:
    p=JsonPointer.from_parts(parts); print(parts,p.path,p.parts)
# Mapping subclass / OrderedDict / defaultdict
dd=collections.defaultdict(list)
try: print(resolve_pointer(dd,'/x','D'), dict(dd))
except Exception as e: print(type(e),e)
# custom __getitem__ raising IndexError/TypeError
class C:
    def __getitem__(self,k): raise IndexError(k)
try: print(resolve_pointer(C(),'/x','D'))
except Exception as e: print('C',type(e).__name__,e)
# set on custom sequence
doc={'a':[1,2]}
print(set_pointer(doc,'/a/1',9,inplace=False), doc)
# deepcopy semantics: shared refs
shared=[1]; doc={'a':shared,'b':shared}
r=set_pointer(doc,'/a/0',5,inplace=False); print(r)
