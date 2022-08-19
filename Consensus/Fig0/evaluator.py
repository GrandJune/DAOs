# -*- coding: utf-8 -*-
# @Time     : 8/9/2022 19:20
# @Author   : Junyi
# @FileName: evaluator.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import matplotlib.pyplot as plt
import pickle

folder = r"C:\Python_Workplace\dao-0815\DAO"
dao_performance_across_time = folder + r"\Fig0\DAO_performance_across_time"
autonomy_performance_across_time = folder + r"\Fig0\Autonomy_performance_across_time"
hierarchy_performance_across_time = folder + r"\Fig0\Hierarchy_performance_across_time"
with open(dao_performance_across_time, 'rb') as in_file:
    data_dao = pickle.load(in_file)
with open(autonomy_performance_across_time, 'rb') as in_file:
    data_autonomy = pickle.load(in_file)
with open(hierarchy_performance_across_time, 'rb') as in_file:
    data_hierarchy = pickle.load(in_file)

# Black-white version
# x = range(len(data_dao))
# plt.plot(x, data_dao, "k-", label="DAO")
# plt.plot(x, data_autonomy, "k--", label="Autonomy")
# plt.plot(x, data_hierarchy, "k:", label="Hierarchy")
# # plt.title('Performance across Iterations')
# plt.xlabel('Iteration', fontweight='bold', fontsize=12)
# plt.ylabel('Performance', fontweight='bold', fontsize=12)
# plt.legend(frameon=False, ncol=1)
# plt.savefig("HAD_comparison.png", transparent=True, dpi=1200)
# plt.show()

# Colorful version
x = range(len(data_dao))
plt.plot(x, data_dao, "r-", label="DAO")
plt.plot(x, data_hierarchy, "b-", label="Hierarchy")
plt.plot(x, data_autonomy, "y-", label="Autonomy")
# plt.title('Performance across Iterations')
plt.xlabel('Iteration', fontweight='bold', fontsize=10)
plt.ylabel('Performance', fontweight='bold', fontsize=10)
plt.legend(frameon=False, ncol=1)
plt.savefig("HAD_comparison.png", transparent=True, dpi=1200)
plt.show()