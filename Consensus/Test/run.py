# -*- coding: utf-8 -*-
# @Time     : 9/23/2022 16:52
# @Author   : Junyi
# @FileName: run.py
# @Software  : PyCharm
# Observing PEP 8 coding style
# from Individual import Individual
from Reality import Reality
# import numpy as np
import time
from DAO import DAO
from Hierarchy import Hierarchy
from Autonomy import Autonomy
import matplotlib.pyplot as plt

t0 = time.time()
m = 120
s = 3
n = 210
lr = 0.3
group_size = 7
search_loop = 300
reality = Reality(m=m, s=s)

dao = DAO(m=m, s=s, n=n, reality=reality, lr=lr)
for _ in range(search_loop):
    dao.search()

hierarchy = Hierarchy(m=m, s=s, n=n, reality=reality, lr=lr)
for _ in range(search_loop):
    hierarchy.search()

autonomy = Autonomy(m=m, s=s, n=n, subgroup_size=group_size, reality=reality, lr=lr)
for _ in range(search_loop):
    autonomy.search()

x = range(search_loop)
plt.plot(x, hierarchy.performance_across_time, "g-", label="Hierarchy")
plt.plot(x, dao.performance_across_time, "r-", label="DAO")
plt.plot(x, autonomy.performance_across_time, "k-", label="Autonomy")
# plt.title('Diversity Decrease')
plt.xlabel('Iteration', fontweight='bold', fontsize=10)
plt.ylabel('Performance', fontweight='bold', fontsize=10)
plt.legend(frameon=False, ncol=3, fontsize=10)
plt.savefig("DHA_performance.png", transparent=False, dpi=1200)
# plt.show()
t1 = time.time()
print(time.strftime("%H:%M:%S", time.gmtime(t1-t0)))

