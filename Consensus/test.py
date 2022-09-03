from Superior import Superior
from Reality import Reality
from Individual import Individual
import matplotlib.pyplot as plt
import numpy as np
import time
# Comparison between Overall Payoff, Policy Payoff, and Belief Payoff
m = 24
s = 3
t_list = [2]
n = 100
data_across_para = []
version = "Weighted"
repetition_round = 1
search_round = 100
t0 = time.time()
for t in t_list:
    data_across_repetition = []
    for _ in range(repetition_round):
        reality = Reality(m=m, s=s, t=t,)
        superior = Superior(m=m, s=s, t=t, n=n, reality=reality, authority=1.0)
        data_across_time = []
        for _ in range(search_round):
            superior.weighted_local_search()
            print(superior.policy)
            payoff_list = [individual.payoff for individual in superior.individuals]
            data_across_time.append(sum(payoff_list) / len(payoff_list))
            print(sum(payoff_list) / len(payoff_list))
        data_across_repetition.append(data_across_time)
    result_1 = []
    for i in range(search_round):
        temp = [payoff_list[i] for payoff_list in data_across_repetition]
        result_1.append(sum(temp) / len(temp))
    data_across_para.append(result_1)


# x = range(search_round)
# plt.plot(x, data_across_para[0], "k-", label="t=1")
# plt.plot(x, data_across_para[1], "k--", label="t=2")
# plt.plot(x, data_across_para[2], "k:", label="t=4")
# # plt.savefig("search.jpg")
# plt.title('Performance Across Strategic Complexity')
# plt.xlabel('Iteration')
# plt.ylabel('Performance')
# plt.legend()
# plt.show()