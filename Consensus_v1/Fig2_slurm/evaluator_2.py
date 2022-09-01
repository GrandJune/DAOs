# -*- coding: utf-8 -*-
# @Time     : 8/9/2022 19:20
# @Author   : Junyi
# @FileName: evaluator.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import matplotlib.pyplot as plt
import pickle


data_folder = r"C:\Python_Workplace\dao-0824\Fig2_slurm"
file_name_1 = data_folder + r"\DAO_diversity_s"
with open(file_name_1, 'rb') as in_file:
    data_1 = pickle.load(in_file)
file_name_2 = data_folder + r"\Hierarchy_diversity_s"
with open(file_name_2, 'rb') as in_file:
    data_2 = pickle.load(in_file)
file_name_3 = data_folder + r"\Autonomy_diversity_s"
with open(file_name_3, 'rb') as in_file:
    data_3 = pickle.load(in_file)
data_1 = [each[-1] for each in data_1]
data_2 = [each[-1] for each in data_2]
data_3 = [each[-1] for each in data_3]
# x = range(len(data[0]))
# plt.plot(x, data[0], "r-", label="s=1")
# plt.plot(x, data[1], "b-", label="s=2")
# plt.plot(x, data[2], "y-", label="s=3")
# plt.plot(x, data[3], "k-", label="s=4")
# plt.plot(x, data[4], "k--", label="s=5")
# plt.title('Diversity Decrease')
x = [1, 2, 3, 4, 5]
plt.plot(x, data_1, "r-", label="DAO")
plt.plot(x, data_2, "b-", label="Hierarchy")
plt.plot(x, data_3, "k--", label="Autonomy")
plt.xlabel('Operational Complexity', fontweight='bold', fontsize=10)
plt.ylabel('Diversity', fontweight='bold', fontsize=10)
plt.legend(frameon=False, fontsize=10)
# plt.xticks(x)
plt.yticks([])
# plt.savefig("Diversity_across_time.png", bbox_inches='tight', pad_inches=0.01, transparent=True, dpi=1200)
# plt.savefig(data_folder + r"\Diversity_across_time.png", bbox_inches='tight', pad_inches=0.01, transparent=True, dpi=1200)
plt.show()
plt.clf()
plt.close()

#  S = 1
# data_folder = r"C:\Python_Workplace\dao-0820\Consensus_1\Fig2_s3"
# file_name_1 = data_folder + r"\DAO_diversity"
# with open(file_name_1, 'rb') as in_file:
#     data_1 = pickle.load(in_file)
# # file_name_2 = data_folder + r"\Hierarchy_diversity"
# # with open(file_name_2, 'rb') as in_file:
# #     data_2 = pickle.load(in_file)
# file_name_3 = data_folder + r"\Autonomy_diversity"
# with open(file_name_3, 'rb') as in_file:
#     data_3 = pickle.load(in_file)
# x = range(len(data_1))
# plt.plot(x, data_1, "r-", label="DAO")
# # plt.plot(x, data_2, "b-", label="Hierarchy")
# plt.plot(x, data_3, "k:", label="Autonomy")
# # plt.title('Diversity Decrease')
# # plt.yticks([])
# plt.xlabel('Iteration', fontweight='bold', fontsize=10)
# plt.ylabel('Diversity', fontweight='bold', fontsize=10)
# plt.legend(frameon=False, ncol=1, fontsize=10)
# plt.savefig(data_folder + r"\Diversity_Dynamics_s3.png", transparent=True, dpi=1200, bbox_inches='tight', pad_inches=0.1,)
# # plt.savefig(r"Diversity_Dynamics_s1.png", transparent=True, dpi=1200, bbox_inches='tight', pad_inches=0.1,)
# plt.show()