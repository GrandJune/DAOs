# -*- coding: utf-8 -*-
# @Time     : 8/9/2022 19:20
# @Author   : Junyi
# @FileName: evaluator.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import matplotlib.pyplot as plt
import pickle


data_folder = r"C:\Python_Workplace\dao-0808\HvsD"
file_name = data_folder + r"\DAO_manager_performance_s135"
print(file_name)
with open(file_name, 'rb') as in_file:
    data = pickle.load(in_file)
# print(data)
x = range(200)
plt.plot(x, data[0], "k-", label="s=1")
plt.plot(x, data[1], "k--", label="s=3")
plt.plot(x, data[2], "k:", label="s=5")
plt.title('Pure Superior Performance')
plt.xlabel('Time')
plt.ylabel('Performance')
plt.legend()
plt.show()
# plt.savefig("Hierarchy_s_pure_superior_performance.jpg")
# plt.clf()
# plt.close()