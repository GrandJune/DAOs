# -*- coding: utf-8 -*-
# @Time     : 2/13/2023 16:22
# @Author   : Junyi
# @FileName: test.py
# @Software  : PyCharm
# Observing PEP 8 coding style
alpha = 3
m = 12
indices = range(m)
lst = list(range(m))
aggregation_rule = [[lst[indices[j]] for j in range(i, i + alpha)] for i in range(0, m, alpha)]
print(aggregation_rule)