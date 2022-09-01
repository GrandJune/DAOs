# -*- coding: utf-8 -*-
# @Time     : 8/9/2022 19:20
# @Author   : Junyi
# @FileName: evaluator.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import matplotlib.pyplot as plt
import pickle


data_folder = r"C:\Python_Workplace\dao-0824\Fig4"
file_name_1 = data_folder + r"\dao_performance_under_turbulence"
with open(file_name_1, 'rb') as in_file:
    data_1 = pickle.load(in_file)
file_name_2 = data_folder + r"\hierarchy_performance_under_turbulence"
with open(file_name_2, 'rb') as in_file:
    data_2 = pickle.load(in_file)
file_name_3 = data_folder + r"\Autonomy_performance_under_turbulence"
with open(file_name_3, 'rb') as in_file:
    data_3 = pickle.load(in_file)
x = range(len(data_1))
plt.plot(x, data_1, "r-", label="DAO")
plt.plot(x, data_2, "b-", label="Hierarchy")
plt.plot(x, data_3, "k--", label="Autonomy")
# plt.title('Diversity Decrease')
plt.xlabel('Iteration', fontweight='bold', fontsize=10)
plt.ylabel('Performance', fontweight='bold', fontsize=10)
plt.yticks([])
plt.legend(frameon=False)
plt.savefig("Turbulence_across_time.png", bbox_inches='tight', pad_inches=0.1, transparent=True, dpi=1200)
plt.savefig(data_folder + r"\Turbulence_across_time.png", bbox_inches='tight', pad_inches=0.1, transparent=True, dpi=1200)
plt.show()
# plt.clf()
# plt.close()
