# -*- coding: utf-8 -*-
# @Time     : 2/7/2023 19:04
# @Author   : Junyi
# @FileName: test.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import random

def divide_list(lst, m):
    n = len(lst)
    indices = random.sample(range(n), n)
    return [[lst[indices[j]] for j in range(i, i + m)] for i in range(0, n, m)]


if __name__ == '__main__':
    res = divide_list(lst=range(60), m=3)
    print(res)