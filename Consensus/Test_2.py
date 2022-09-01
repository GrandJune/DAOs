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

# import dirichlet
import numpy as np
import matplotlib.pyplot as plt

# Using dirichlet() method
gfg = np.random.dirichlet((3, 1, 1), size=1000)

count, bins, ignored = plt.hist(gfg, 30, density=True)
plt.show()
