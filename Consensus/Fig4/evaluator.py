# -*- coding: utf-8 -*-
# @Time     : 8/9/2022 19:20
# @Author   : Junyi
# @FileName: evaluator.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import matplotlib.pyplot as plt
import pickle


data_folder = r"C:\Python_Workplace\dao-0820\Consensus\Fig3"
file_name_1 = data_folder + r"\DAO_diversity"
with open(file_name_1, 'rb') as in_file:
    data_1 = pickle.load(in_file)
file_name_2 = data_folder + r"\Hierarchy_diversity"
with open(file_name_2, 'rb') as in_file:
    data_2 = pickle.load(in_file)
file_name_3 = data_folder + r"\Autonomy_diversity"
with open(file_name_3, 'rb') as in_file:
    data_3 = pickle.load(in_file)
x = range(len(data_1))
plt.plot(x, data_1, "r-", label="DAO")
plt.plot(x, data_2, "b-", label="Hierarchy")
plt.plot(x, data_3, "k-", label="Autonomy")
# plt.title('Diversity Decrease')
plt.xlabel('Iteration', fontweight='bold', fontsize=10)
plt.ylabel('Diversity', fontweight='bold', fontsize=10)
plt.legend(frameon=False, ncol=3, fontsize=10)
plt.savefig("Diversity_Comparison_s3.png", transparent=True, dpi=1200)
plt.show()
# plt.clf()
# plt.close()

#  S = 1
data_folder = r"C:\Python_Workplace\dao-0815\Fig2_s=1"
file_name_1 = data_folder + r"\DAO_diversity"
with open(file_name_1, 'rb') as in_file:
    data_1 = pickle.load(in_file)
file_name_2 = data_folder + r"\Hierarchy_diversity"
with open(file_name_2, 'rb') as in_file:
    data_2 = pickle.load(in_file)
file_name_3 = data_folder + r"\Autonomy_diversity"
with open(file_name_3, 'rb') as in_file:
    data_3 = pickle.load(in_file)
x = range(len(data_1))
plt.plot(x, data_1, "r-", label="DAO")
plt.plot(x, data_2, "b-", label="Hierarchy")
plt.plot(x, data_3, "k-", label="Autonomy")
# plt.title('Diversity Decrease')
plt.xlabel('Iteration', fontweight='bold', fontsize=10)
plt.ylabel('Diversity', fontweight='bold', fontsize=10)
plt.legend(frameon=False, ncol=3, fontsize=10)
plt.savefig("Diversity_Comparison_s1.png", transparent=True, dpi=1200)
plt.show()