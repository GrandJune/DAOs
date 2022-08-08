from multiprocessing import Pool
m = 120
s = 7
t = 2
if m % (s * t) != 0:
    m = s * t * (m // s // t)
print(m)