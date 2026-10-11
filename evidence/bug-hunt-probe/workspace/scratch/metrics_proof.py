import sys; sys.path.insert(0,'.')
import metrics, math
d=[1,2,3,4,5,6,7,8,9,10]
print("p50 of 1..10 (expect 5):", metrics.percentile(d,50))
print("p10 (expect 1):", metrics.percentile(d,10))
print("p100 (expect 10):", metrics.percentile(d,100))
print("p70 (expect 7):", metrics.percentile(d,70), 70/100*10)
v=[3,1,2]; metrics.percentile(v,50); print("mutation:", v)
for bad in ([],):
    try: metrics.percentile(bad,50)
    except ValueError: print("empty ok")
for p in (-1,101):
    try: metrics.percentile(d,p)
    except ValueError: print("bad p ok",p)
print("p0:", metrics.percentile([5,3,9],0))
print("ma:", metrics.moving_average([1,2,3,4],2), metrics.moving_average([1],2))
v=[1,2,3]; metrics.moving_average(v,2); print(v)
for w in (0,-1,2.0):
    try: metrics.moving_average([1,2,3],w); print("no error",w)
    except ValueError: print("ok",w)
print("drift:", metrics.moving_average([1e16,1,1,1,1e16],2)[1:3], "expect [1.0,1.0]")
