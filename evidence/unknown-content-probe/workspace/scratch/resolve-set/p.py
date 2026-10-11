import sys
sys.path.insert(0, '/research/claude-workflow-research/unknown-content-probe/workspace')
from jsonpointer import *
import jsonpointer, copy
def t(label, f):
    try: print(label, '->', repr(f()))
    except BaseException as e: print(label, 'EXC', type(e).__name__, e)
L=[10,20,30]
for p in ['/0','/00','/-0','/+1','/1.0','/ 1','/1 ','/١','/²','/','/1\n','/-','/3','/-1','/10000000000000000000','/０']:
    t('list '+repr(p), lambda: resolve_pointer(L,p))
t('d default list',lambda: resolve_pointer(L,'/9','D'))
t('d default type',lambda: resolve_pointer(5,'/9','D'))
t('empty key',lambda: resolve_pointer({'':{'':1}},'//'))
t('root str',lambda: resolve_pointer('abc',''))
t('default falsy',lambda: resolve_pointer({}, '/a', 0))
# escape
d={'~1':1,'/':2,'~':3,'a~1b':4,'~01':5}
for p in ['/~001','/~01','/~1','/~0','/~01','/a~01b','/~0~1','/~00']:
    t(p, lambda: resolve_pointer({'~1':'tilde1','/':'slash','~':'tilde','~01':'x','~/':'tildeslash','~0':'t0'},p))
# set
t('set tuple -',lambda: set_pointer({'a':(1,2)},'/a/-',3))
t('set tuple idx',lambda: set_pointer({'a':(1,2)},'/a/0',3))
t('set oob',lambda: set_pointer([1],'/5',3))
t('set idx==len',lambda: set_pointer([1],'/1',3))
t('set - dict',lambda: set_pointer({'a':1},'/-',3))
t('set str parent',lambda: set_pointer({'a':'xyz'},'/a/0','q'))
t('set root noinplace',lambda: set_pointer([1],'',[2],inplace=False))
t('set - nested', lambda: set_pointer({'a':[1]},'/a/-/b',1))
t('set - middle noinplace', lambda: set_pointer({'a':[1]},'/a/-',[]))
doc={'a':[1]}; r=set_pointer(doc,'/a/0',2,inplace=True); print(r is doc)
doc={'a':[1]}; r=set_pointer(doc,'/a/0',2,inplace=False); print(r is doc, doc, r)
v=[1]; doc={'a':1}; r=set_pointer(doc,'/b',v,inplace=False); print(r['b'] is v)
doc={'a':[1]}
t('set fail noinplace unchanged', lambda: set_pointer(doc,'/a/5/x',1,inplace=False)); print(doc)
# to_last
t('to_last -',lambda: JsonPointer('/a/-').to_last({'a':[1]}))
t('to_last oob',lambda: JsonPointer('/a/9').to_last({'a':[1]}))
t('to_last missing',lambda: JsonPointer('/a/b').to_last({'a':{}}))
t('to_last list key',lambda: JsonPointer('/a/x').to_last({'a':[1]}))
t('get_part',lambda: JsonPointer.get_part([1],'01'))
t('get_part int',lambda: JsonPointer.get_part([1],1))
# resolve default with EndOfList
t('eol',lambda: resolve_pointer({'a':[1]},'/a/-','d'))
t('eol-1',lambda: resolve_pointer({'a':[1]},'/a/-/0','d'))
t('walk oob',lambda: JsonPointer('/a').walk([1],'5'))
t('invalid no slash default',lambda: resolve_pointer({}, 'a', 'd'))
t('bytes',lambda: resolve_pointer({'a':b'xy'},'/a/0'))
t('tuple',lambda: resolve_pointer({'a':(1,2)},'/a/1'))
t('str key digits',lambda: resolve_pointer({'01':1},'/01'))
t('nested None',lambda: resolve_pointer({'a':None},'/a/b','d'))
t('ptr trailing newline',lambda: JsonPointer('/a\n').parts)
t('~ newline',lambda: JsonPointer('/a~\n').parts)
t('ptr nonstr',lambda: JsonPointer(None))
t('verbose',lambda: resolve_pointer({'a':1},'/b'))
