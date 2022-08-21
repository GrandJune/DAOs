# -*- coding: utf-8 -*-
# @Time     : 8/9/2022 19:20
# @Author   : Junyi
# @FileName: evaluator.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import matplotlib.pyplot as plt
import pickle


data_folder = r"C:\Python_Workplace\dao-0820\Consensus_1\Fig1"
file_name_1 = data_folder + r"\DAO_performance_s_1"
with open(file_name_1, 'rb') as in_file:
    data_1 = pickle.load(in_file)
file_name_2 = data_folder + r"\DAO_performance_s_2"
with open(file_name_1, 'rb') as in_file:
    data_2 = pickle.load(in_file)
dao_data = data_1 + data_2
dao_across_s = [each[-1] for each in dao_data]

file_name_3 = data_folder + r"\Autonomy_performance_s"
with open(file_name_1, 'rb') as in_file:
    data_3 = pickle.load(in_file)

autonomy_across_s = [each[-1] for each in data_3]

file_name_4 = data_folder + r"\Hierarchy_performance_s"
with open(file_name_1, 'rb') as in_file:
    data_4 = pickle.load(in_file)

hierarchy_across_s = [each[-1] for each in data_4]


x = range(len(autonomy_across_s))

plt.plot(x, dao_across_s, "k-", label="DAO")
plt.plot(x, autonomy_across_s, "k--", label="Autonomy")
plt.plot(x, hierarchy_across_s, "k:", label="Hierarchy")
# plt.plot(x, data_1[2], "b-", label="s=7")
# plt.plot(x, data_1[2], "r-", label="s=9")
# plt.title('Pure Superior Performance')
plt.xlabel('Operational Complexity', fontweight='bold', fontsize=10)
plt.ylabel('Performance', fontweight='bold', fontsize=10)
plt.legend(frameon=False, ncol=1)
# plt.savefig("Performance_across_s.png")
plt.show()
# plt.clf()
# plt.close()