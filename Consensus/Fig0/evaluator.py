# -*- coding: utf-8 -*-
# @Time     : 8/9/2022 19:20
# @Author   : Junyi
# @FileName: evaluator.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import matplotlib.pyplot as plt
import pickle


dao_performance_across_time = r"C:\Python_Workplace\dao-0810\Fig0\DAO_performance_across_time"
autonomy_performance_across_time = r"C:\Python_Workplace\dao-0810\Fig0\Autonomy_performance_across_time"
hierarchy_performance_across_time = r"C:\Python_Workplace\dao-0810\Fig0\Hierarchy_performance_across_time"
with open(dao_performance_across_time, 'rb') as in_file:
    data_dao = pickle.load(in_file)
with open(dao_performance_across_time, 'rb') as in_file:
    data_autonomy = pickle.load(in_file)
with open(dao_performance_across_time, 'rb') as in_file:
    data_hierarchy = pickle.load(in_file)

x = range(500)
# plt.plot(x, data_dao, "k-", label="DAO")
# plt.plot(x, data_autonomy, "k--", label="Autonomy")
plt.plot(x, data_hierarchy, "k:", label="Hierarchy")
plt.title('Performance across Iterations')
plt.xlabel('Time')
plt.ylabel('Performance')
plt.legend()
plt.show()
# plt.savefig("Hierarchy_s_pure_superior_performance.jpg")
# plt.clf()
# plt.close()