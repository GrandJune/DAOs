# -*- coding: utf-8 -*-
# @Time     : 6/6/2022 21:36
# @Author   : Junyi
# @FileName: test.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
from Reality import Reality
from Individual import Individual
import math
n = 200
subgroup_size = 40
cluster_num = math.ceil(n / subgroup_size)
beta = 0.2
print(cluster_num)
# for i in range(n):
#     x = i // subgroup_size
#     # other_clusters = list(range(cluster_num))
#     # other_clusters.remove(0)
#     # print(other_clusters)
#     print(x)
#     # if np.random.uniform(0, 1) < beta:
#     #     other_clusters = list(range(cluster_num)).remove(i % subgroup_size)
#     #     cluster_index = np.random.choice(other_clusters, p=[1 / len(other_clusters)] * len(other_clusters))
#     #     print(cluster_index)

# network = np.diag(range(10))
# network = [[1, 0, 0],
#            [0, 1, 0],
#            [0, 0, 1]]
# network = np.array(network)
# print(network)
# free_space = np.array(np.where(network == 0))
# element = network[np.where(network == 0)]
# print(free_space)
# print(element)
import matplotlib.pyplot as plt
x = range(10)
y = np.arange(10, 20)
l1=plt.plot(x, y, 'k-.',label='z=7')
plt.plot(x, y+1, 'k:',label='z=2')
plt.plot(x, y+2, 'k--',label='z=2')
plt.plot(x, y*2, 'k-',label='z=2')
plt.title('Effect of Subgroup Size on Organizational Performance')
plt.xlabel('beta')
plt.ylabel('Performance')
plt.legend()
plt.show()