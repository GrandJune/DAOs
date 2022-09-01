# -*- coding: utf-8 -*-
# @Time     : 8/9/2022 19:20
# @Author   : Junyi
# @FileName: evaluator.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import matplotlib.pyplot as plt
import pickle


data_folder = r"C:\Python_Workplace\dao-0808\HvsD"
file_name_1 = data_folder + r"\DAO_performance_s"
with open(file_name_1, 'rb') as in_file:
    data_1 = pickle.load(in_file)
# print(data)
x = range(200)
plt.plot(x, data_1, "k-", label="DAO")
plt.plot(x, data_1[1], "k--", label="s=3")
plt.plot(x, data_1[2], "k:", label="s=5")
plt.title('Pure Superior Performance')
plt.xlabel('Operational Complexity', fontweight='bold', fontsize=12)
plt.ylabel('Performance', fontweight='bold', fontsize=12)
plt.legend(frameon=False, ncol=1)

plt.savefig("Performance_across_s.png")
plt.show()
# plt.clf()
# plt.close()