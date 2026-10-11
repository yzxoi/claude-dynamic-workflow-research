import sys, itertools, doctest
sys.path.insert(0, '/research/claude-workflow-research/unknown-content-probe/workspace')
import jsonpointer as jp
from jsonpointer import *
print(doctest.testmod(jp))
def t(label, f):
    try: print(label, '->', repr(f()))
    except BaseException as e: print(label, 'EXC', type(e).__name__, e)
# exhaustive roundtrip
bad=0
alpha='~01/a\n'
for n in range(0,6):
    for tup in itertools.product(alpha, repeat=n):
        s=''.join(tup)
        valid = True
        try: p=JsonPointer(s)
        except JsonPointerException: valid=False; continue
        if p.path!=s: print('path mismatch',repr(s),p.path); bad+=1
        if JsonPointer.from_parts(p.parts)!=p: print('from_parts mismatch',repr(s)); bad+=1
        if hash(JsonPointer(p.path))!=hash(p): bad+=1
print('bad',bad)
# escape/unescape round trip on arbitrary parts
for n in range(0,5):
    for tup in itertools.product('~01/', repeat=n):
        s=''.join(tup)
        assert unescape(escape(s))==s, s
        p=JsonPointer.from_parts([s]); assert p.parts==[s], (s,p.parts)
# which strings are rejected? compare with RFC grammar
import re
rfc=re.compile(r'(?s)(?:/(?:[^/~]|~[01])*)*\Z')
for n in range(0,6):
    for tup in itertools.product('~01/a\n', repeat=n):
        s=''.join(tup)
        try: JsonPointer(s); ok=True
        except JsonPointerException: ok=False
        if ok!=bool(rfc.match(s)): print('validity mismatch',repr(s),ok)
p=JsonPointer('/a/b/c')
t('join str no slash', lambda: p.join('d'))
t('join empty str', lambda: p.join('').path)
t('join [""]', lambda: p.join(['']).path)
t('join ["a/b"]', lambda: p.join(['a/b']).path)
t('join [1,2]', lambda: p.join([1,2]).path)
t('join tuple', lambda: p.join(('x','~')).path)
t('join bad str', lambda: p.join('/a~'))
t('join None', lambda: p.join(None))
t('join bytes', lambda: p.join(b'/a'))
t('div str', lambda: (p/'/x').path)
t('div int', lambda: p/1)
t('rdiv', lambda: '/x'/p)
t('root contains', lambda: (p.contains(JsonPointer('')), JsonPointer('').contains(p)))
t('contains str', lambda: p.contains('/a'))
t('in str', lambda: '/a' in p)
t('eq sub', lambda: JsonPointer('/a')==type('P',(JsonPointer,),{})('/a'))
t('ne', lambda: JsonPointer('/a')!=JsonPointer('/a'))
t('eq escaped', lambda: JsonPointer('/a~1b')==JsonPointer.from_parts(['a/b']))
t('frag', lambda: JsonPointer('#/a'))
t('frag2', lambda: JsonPointer('#'))
t('nonstr', lambda: JsonPointer(None))
t('list', lambda: JsonPointer(['a']))
t('from_parts str', lambda: JsonPointer.from_parts('ab').parts)
t('from_parts empty', lambda: JsonPointer.from_parts([]).path)
t('from_parts [""]', lambda: JsonPointer.from_parts(['']).path)
t('from_parts none', lambda: JsonPointer.from_parts([None]).parts)
t('from_parts gen', lambda: JsonPointer.from_parts(x for x in 'ab').path)
q=JsonPointer('/a/b'); q.get_parts().append('z'); t('mutation', lambda: (q.path, str(q)))
t('join no mutate', lambda: (p.join(['x']), p))
t('set-eq hash', lambda: len({JsonPointer('/a'),JsonPointer('/a'),JsonPointer('/b')}))
t('unicode', lambda: JsonPointer('/\ud800').path)
t('repr subclass', lambda: repr(type('P',(JsonPointer,),{})('/a')))
t('str of root', lambda: (str(JsonPointer('')), repr(JsonPointer(''))))
t('join sub-prefix contain', lambda: JsonPointer('/ab').contains(JsonPointer('/a')))
t('contains mixed escapes', lambda: JsonPointer('/a~1b/c').contains(JsonPointer('/a')))
