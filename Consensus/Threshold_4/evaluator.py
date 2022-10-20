# -*- coding: utf-8 -*-
# @Time     : 10/14/2022 17:06
# @Author   : Junyi
# @FileName: evaluator.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import matplotlib.pyplot as plt
from matplotlib import container
import pickle
import numpy as np


data_folder = r"E:\data\gst-1014\Threshold"
dao_performance_file = data_folder + r"\dao_performance_across_threshold"
# s_performance_file = data_folder + r"\s_performance_across_K"
# t_performance_file = data_folder + r"\t_performance_across_K"
with open(dao_performance_file, 'rb') as infile:
    dao_performance = pickle.load(infile)
# with open(s_performance_file, 'rb') as infile:
#     s_performance = pickle.load(infile)
# with open(t_performance_file, 'rb') as infile:
#     t_performance = pickle.load(infile)

x = np.arange(0, 0.30, 0.05)
fig, (ax1) = plt.subplots(1, 1)
ax1.errorbar(x, dao_performance, yerr=0.1, color="g", fmt="--", capsize=5, capthick=0.8, ecolor="g", label="DAO")
plt.xlabel('Threshold', fontweight='bold', fontsize=10)
plt.ylabel('Performance', fontweight='bold', fontsize=10)
plt.xticks(x)
handles, labels = ax1.get_legend_handles_labels()
handles = [h[0] if isinstance(h, container.ErrorbarContainer) else h for h in handles]
plt.legend(handles, labels, loc='upper left', numpoints=1)

# plt.legend(frameon=False, ncol=3, fontsize=10)
plt.show()
# plt.savefig("Performance_across_threshold.png", transparent=True, dpi=200)
plt.clf()
# print(time.strftime("%H:%M:%S", time.gmtime(t1 - t0)))
