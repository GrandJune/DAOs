from multiprocessing import Pool
import time

# t0 = time.time()
# m = 120
# s = 7
# t = 2
# if m % (s * t) != 0:
#     m = s * t * (m // s // t)
# # print(m)
# t1 = time.time()
# run_time = t1-t0
# run_time = time.strftime("%H:%M:%S", time.gmtime(run_time))
# print(run_time)

x = range(10)
x_1 = x[5::]
print(x_1)