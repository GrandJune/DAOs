# -*- coding: utf-8 -*-
# @Time     : 8/5/2022 21:49
# @Author   : Junyi
# @FileName: test.py
# @Software  : PyCharm
# Observing PEP 8 coding style
from Superior import Superior
from Reality import Reality
from Individual import Individual
import matplotlib
# matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np
import time
import pickle
#
#
# x = range(100)
# y = [2*i for i in x]
# plt.plot(x, y, "b-", label="a=0.1")
# plt.title('Superior Performance')
# plt.xlabel('Time')
# plt.ylabel('Performance')
# plt.legend()
# plt.savefig("Exp_alpha_superior_performance.jpg")
# print("Test")

m = 120
s = 5
policy_number = m // s
flag = 0
for _ in range(100):
    focal_index = np.random.randint(0, policy_number)
    print(policy_number, focal_index)
    if policy_number == focal_index:
        flag = 1
print(flag)