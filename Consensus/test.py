# -*- coding: utf-8 -*-
# @Time     : 6/11/2022 21:13
# @Author   : Junyi
# @FileName: test.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
from itertools import permutations

x = [1, 0, 1]
# generate permutations for x
permutations_x = permutations(x)
for each in permutations_x:
    print(each)