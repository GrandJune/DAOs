# -*- coding: utf-8 -*-
# @Time     : 8/9/2022 19:20
# @Author   : Junyi
# @FileName: evaluator.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import matplotlib.pyplot as plt
import pickle


# data_folder = r"C:\Python_Workplace\dao-0808\HvsD"
# file_name_1 = data_folder + r"\DAO_performance_s"
# with open(file_name_1, 'rb') as in_file:
#     data_1 = pickle.load(in_file)
# # print(data)
# x = range(200)
# plt.plot(x, data_1, "k-", label="DAO")
# plt.plot(x, data_1[1], "k--", label="s=3")
# plt.plot(x, data_1[2], "k:", label="s=5")
# plt.title('Pure Superior Performance')
# plt.xlabel('Operational Complexity', fontweight='bold', fontsize=12)
# plt.ylabel('Performance', fontweight='bold', fontsize=12)
# plt.legend(frameon=False, ncol=1)
#
# plt.savefig("Performance_across_s.png")
# plt.show()
# plt.clf()
# plt.close()


# Crowd Size
# folder = r"C:\Python_Workplace\dao-0824\Consensus\Robust"
# file_name_1 = folder + r"\robust_performance_across_n"
# with open(file_name_1, 'rb') as in_file:
#     data_1 = pickle.load(in_file)
# # print(data)
# # [10, 50, 100, 150, 200]
# # data_1 = [each[-1] for each in data_1]
# # x = [10, 50, 100, 150, 200]
# x = range(len(data_1[0]))
# # plt.plot(x, data_1, "k-", label="DAO")
# # plt.plot(x, data_1[0], "b-", label="10")
# plt.plot(x, data_1[1], "y-", label="50")
# plt.plot(x, data_1[1], "r-", label="100")
# # plt.plot(x, data_1[1], "k-", label="150")
# plt.plot(x, data_1[1], "k--", label="200")
# plt.title('Group Size Effect')
# plt.xlabel('Group Size', fontweight='bold', fontsize=12)
# plt.ylabel('Performance', fontweight='bold', fontsize=12)
# plt.legend(frameon=False, ncol=1)
# plt.savefig("Performance_across_n.png", transparent=True, dpi=1200)
# plt.savefig(folder + r"\Performance_across_n.png", transparent=True, dpi=1200)
# plt.show()


# Problem Dimension
# folder = r"C:\Python_Workplace\dao-0824\Consensus\Robust"
# file_name_1 = folder + r"\robust_performance_across_m"
# with open(file_name_1, 'rb') as in_file:
#     data_1 = pickle.load(in_file)
# # print(data)
# # [10, 50, 100, 150, 200]
# # data_1 = [each[-1] for each in data_1]
# # x = [30, 60, 90]
# x = range(len(data_1[-1]))
# for each_data in data_1:
#     if len(each_data) < len(data_1[-1]):
#         each_data += [each_data[-1]] * (len(data_1[-1]) - len(each_data))
#
# # x_0 = range(len(data_1[0]))
# # x_1 = range(len(data_1[1]))
# # x_2 = range(len(data_1[2]))
# # plt.plot(x, data_1, "k-", label="DAO")
# plt.plot(x, data_1[0], "b-", label="30")
# plt.plot(x, data_1[1], "y-", label="60")
# plt.plot(x, data_1[2], "r-", label="90")
#
# plt.title('Problem Dimension Effect')
# plt.xlabel('Problem Dimension', fontweight='bold', fontsize=12)
# plt.ylabel('Performance', fontweight='bold', fontsize=12)
# plt.legend(frameon=False, ncol=1)
# plt.savefig("Performance_across_m.png", transparent=True, dpi=1200)
# plt.savefig(folder + r"\Performance_across_m.png", transparent=True, dpi=1200)
# plt.show()


# T-test
