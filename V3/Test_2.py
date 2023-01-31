from multiprocessing import Pool
import time
import multiprocessing as mp
from multiprocessing import pool


# def worker(s, ):
#     print(str(s) + "s represent!")
#     return range(s)
#
#
#
# if __name__ == "__main__":
#     cpu_num = mp.cpu_count()
#     print("cpu_num: ", cpu_num)
#     pool = Pool(cpu_num)
#     result_list = []
#     for i in range(20):
#         result_list.append(pool.apply_async(func=worker, args=(i, )).get())
#         print("********")
#     print(result_list)

import numpy as np
import math
import matplotlib.pyplot as plt
from itertools import product

# weight_list = []
# for i in range(1000):
#     weight_list.append(np.random.normal(loc=0, scale=0.4))
# # weight_list = [abs(each) for each in weight_list]
# count, bins, ignored = plt.hist(weight_list)
# plt.show()
# test = [1, -1]
# s = list(product(test, repeat=3))
# # s = [each for each in s if sum(each) > 0]
# print(s)

# import numpy as np

res = []
for i in range(10000):
    a = np.random.uniform(0, 1)
    b = 0
    c = 0
    while b < a:
         c += 1
         b = np.random.uniform(0, 1)
    # print(c)
    res.append(c)

max_data = max(res)
bins = np.linspace(0, max_data, max_data+1)
import matplotlib.pyplot as plt
plt.clf()
plt.hist(res, bins)
# plt.xticks(range(0, 100))
plt.show()
print(np.mean(res))
# print("Test")