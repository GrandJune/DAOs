# -*- coding: utf-8 -*-
# @Time     : 8/9/2022 19:20
# @Author   : Junyi
# @FileName: evaluator.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import matplotlib.pyplot as plt
import pickle


folder = r"C:\Python_Workplace\dao-0820\Consensus\Fig1"
file_name_dao = folder + r"\DAO_performance_across_s"
with open(file_name_dao, 'rb') as in_file:
    data_dao = pickle.load(in_file)

file_name_autonomy = folder + r"\Autonomy_performance_across_s"
with open(file_name_autonomy, 'rb') as in_file:
    data_autonomy = pickle.load(in_file)

file_name_hierarchy = folder + r"\Hierarchy_performance_across_s"
with open(file_name_hierarchy, 'rb') as in_file:
    data_hierarchy = pickle.load(in_file)

# data_dao = [each[-1] for each in data_dao]
# data_autonomy = [each[-1] for each in data_autonomy]
# data_hierarchy = [each[-1] for each in data_hierarchy]
#
# x = range(len(data_dao))
#
# plt.plot(x, data_dao, "k-", label="DAO")
# plt.plot(x, data_autonomy, "k--", label="Autonomy")
# plt.plot(x, data_hierarchy, "k:", label="Hierarchy")
# plt.xlabel('Operational Complexity', fontweight='bold', fontsize=10)
# plt.ylabel('Performance', fontweight='bold', fontsize=10)
# plt.legend(frameon=False, ncol=1)
# plt.savefig("HAD_across_s.png", transparent=True, dpi=1200)
# plt.savefig(folder + r"\HAD_across_s.png", transparent=True, dpi=1200)
# plt.show()

# Test the round
# x = range(len(data_hierarchy[0]))
#
# plt.plot(x, data_hierarchy[-3], "k-", label="s1")
# plt.plot(x, data_hierarchy[-2], "k--", label="s2")
# plt.plot(x, data_hierarchy[-1], "k:", label="s2")
# plt.show()