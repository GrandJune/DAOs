# -*- coding: utf-8 -*-
# @Time     : 5/18/2023 17:21
# @Author   : Junyi
# @FileName: test.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
asymmetry = 1
mode = 10
for _ in range(10):
    test = (np.random.pareto(a=asymmetry) + 1) * mode
    print(test)