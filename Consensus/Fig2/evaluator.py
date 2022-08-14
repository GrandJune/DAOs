# -*- coding: utf-8 -*-
# @Time     : 8/9/2022 19:20
# @Author   : Junyi
# @FileName: evaluator.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import matplotlib.pyplot as plt
import pickle


data_folder = r"C:\Python_Workplace\dao-0810\Fig2"
file_name_1 = data_folder + r"\DAO_diversity"
with open(file_name_1, 'rb') as in_file:
    data_1 = pickle.load(in_file)
file_name_2 = data_folder + r"\Hierarchy_diversity"
with open(file_name_2, 'rb') as in_file:
    data_2 = pickle.load(in_file)
x = range(len(data_1))
plt.plot(x, data_1, "k-", label="DAO")
plt.plot(x, data_2, "k--", label="s=3")
plt.title('Diversity Decrease')
plt.xlabel('Time')
plt.ylabel('Diversity')
plt.legend()
plt.savefig("Diversity_Comparison.jpg")
plt.show()
# plt.clf()
# plt.close()