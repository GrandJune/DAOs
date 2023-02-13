import matplotlib.pyplot as plt
import numpy as np


alpha = 3
m = 12
indices = range(m)
lst = list(range(m))
aggregation_rule = [[lst[indices[j]] for j in range(i, i + alpha)] for i in range(0, m, alpha)]
print(aggregation_rule)