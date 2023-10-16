# -*- coding: utf-8 -*-
# @Time     : 3/9/2023 20:49
# @Author   : Junyi
# @FileName: test.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
import math
m = 10
correct_num = 5

for _ in range(10):
    correct_indexes = np.random.choice(range(m), correct_num, replace=False).tolist()
    print(correct_indexes)
    del correct_indexes
