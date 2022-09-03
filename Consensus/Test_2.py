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

weight_list = []
for i in range(1000):
    weight_list.append(np.random.normal(loc=0, scale=0.4))
# weight_list = [abs(each) for each in weight_list]
count, bins, ignored = plt.hist(weight_list)
plt.show()