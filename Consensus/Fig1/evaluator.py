# -*- coding: utf-8 -*-
# @Time     : 8/9/2022 19:20
# @Author   : Junyi
# @FileName: evaluator.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import matplotlib.pyplot as plt
import pickle


data_folder = r"C:\Python_Workplace\dao-0820\Consensus"
file_name_1 = data_folder + r"\Fig1\DAO_performance_s_1"
with open(file_name_1, 'rb') as in_file:
    data_1 = pickle.load(in_file)
file_name_2 = data_folder + r"\Fig1\DAO_performance_s_2"
with open(file_name_1, 'rb') as in_file:
    data_2 = pickle.load(in_file)
data_1 = data_1 + data_2
# data_folder = r"C:\Python_Workplace\dao-0808\HvsD"
# file_name_1 = data_folder + r"\DAO_performance_s"
# with open(file_name_1, 'rb') as in_file:
#     data_1 = pickle.load(in_file)
x = range(len(data_1[0]))
plt.plot(x, data_1[0], "k-", label="s=1")
plt.plot(x, data_1[1], "k--", label="s=3")
plt.plot(x, data_1[2], "k:", label="s=5")
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