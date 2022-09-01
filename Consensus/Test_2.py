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
weight_list = []
for _ in range(100):
    weight = np.random.normal(1, 0.1)
    weight_list.append(weight)

# plt.hist(weight_list)
# plt.show()


n, bins, patches = plt.hist(weight_list, 50, density=True, facecolor='g', alpha=0.75)


plt.xlabel('Smarts')
plt.ylabel('Probability')
plt.title('Histogram of IQ')
plt.text(60, .025, r'$\mu=100,\ \sigma=15$')
plt.xlim(40, 160)
plt.ylim(0, 0.03)
plt.grid(True)
plt.show()