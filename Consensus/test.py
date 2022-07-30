from Superior import Superior
from Reality import Reality
from Individual import Individual
import matplotlib.pyplot as plt
import numpy as np
import time


# Comparison between Overall Payoff, Policy Payoff, and Belief Payoff
m = 24
s = 3
t = 2
n = 100
alpha_list = [0.1, 0.5, 0.9]
overall_across_para = []
manager_across_para = []
superior_across_para = []
version = "Rushed"
t0 = time.time()
for alpha in alpha_list:
    overall_payoff_across_repeat = []
    manager_payoff_across_repeat = []
    superior_payoff_across_repeat = []
    for _ in range(500):
        reality = Reality(m=m, s=s, t=t, alpha=alpha)
        superior = Superior(m=m, s=s, t=t, n=n, reality=reality)
        superior.policy = []  # remove the policy
        overall_payoff_across_time = []
        manager_payoff_across_time = []
        superior_payoff_across_time = []
        for _ in range(100):
            for individual in superior.individuals:
                individual.free_local_search(version=version)
            overall_performance = [alpha * individual.payoff + (1-alpha) * individual.policy_payoff for individual in superior.individuals]
            manager_performance = [individual.payoff for individual in superior.individuals]
            policy_performance = [individual.policy_payoff for individual in superior.individuals]
            overall_payoff_across_time.append(sum(overall_performance) / len(overall_performance))
            manager_payoff_across_time.append(sum(manager_performance) / len(manager_performance))
            superior_payoff_across_time.append(sum(policy_performance) / len(policy_performance))

        for index in range(int(m/s)):
            for individual in superior.individuals:
                individual.policy = []  # reset the policy dummy
                for i in range(m // s):
                    temp = sum(individual.belief[index] for index in range(i * s, (i + 1) *s))
                    if temp < 0:
                        individual.policy.append(-1)
                    else:
                        individual.policy.append(1)
            temp = sum([individual.policy[index] for individual in superior.individuals])
            if temp > 0:
                superior.policy.append(1)  # fake superior as the consensus
            elif temp == 0:
                superior.policy.append(0)
            else:
                superior.policy.append(-1)
        for _ in range(20):  # we don't need loop here.
            for index, value in enumerate(superior.policy):
                for individual in superior.individuals:
                    individual.constrained_local_search(focal_policy=value, focal_policy_index=index, version=version)
            overall_performance = [alpha * individual.payoff + (1-alpha) * superior.payoff for individual in superior.individuals]
            manager_performance = [individual.payoff for individual in superior.individuals]
            policy_performance = [individual.policy_payoff for individual in superior.individuals]
            overall_payoff_across_time.append(sum(overall_performance) / len(overall_performance))
            manager_payoff_across_time.append(sum(manager_performance) / len(manager_performance))
            superior_payoff_across_time.append(sum(policy_performance) / len(policy_performance))
        overall_payoff_across_repeat.append(overall_payoff_across_time)
        manager_payoff_across_repeat.append(manager_payoff_across_time)
        superior_payoff_across_repeat.append(superior_payoff_across_time)
    result_0 = []
    for index in range(len(overall_payoff_across_repeat[0])):
        temp = [payoff_list[index] for payoff_list in overall_payoff_across_repeat]
        result_0.append(sum(temp) / len(temp))
    overall_across_para.append(result_0)
    result_1 = []
    for index in range(len(manager_payoff_across_repeat[0])):
        temp = [payoff_list[index] for payoff_list in manager_payoff_across_repeat]
        result_1.append(sum(temp) / len(temp))
    manager_across_para.append(result_1)
    result_2 = []
    for index in range(len(superior_payoff_across_repeat[0])):
        temp = [payoff_list[index] for payoff_list in superior_payoff_across_repeat]
        result_2.append(sum(temp) / len(temp))
    superior_across_para.append(result_2)


x = range(120)
plt.plot(x, overall_across_para[0], "k-", label="alpha=0.1")
plt.plot(x, overall_across_para[1], "k--", label="alpha=0.5")
plt.plot(x, overall_across_para[2], "k:", label="alpha=0.9")
# plt.savefig("search.jpg")
plt.title('Overall Performance')
plt.xlabel('Time')
plt.ylabel('Performance')
plt.legend()
# plt.show()
plt.savefig("Overall_Performance.jpg")

# Only managers
x = range(120)
plt.plot(x, manager_across_para[0], "k-", label="alpha=0.1")
plt.plot(x, manager_across_para[1], "k--", label="alpha=0.5")
plt.plot(x, manager_across_para[2], "k:", label="alpha=0.9")
# plt.savefig("search.jpg")
plt.title('Manager Performance')
plt.xlabel('Time')
plt.ylabel('Performance')
plt.legend()
# plt.show()
plt.savefig("Manager_Performance.jpg")

# Only superior
# Only managers
x = range(120)
plt.plot(x, superior_across_para[0], "k-", label="alpha=0.1")
plt.plot(x, superior_across_para[1], "k--", label="alpha=0.5")
plt.plot(x, superior_across_para[2], "k:", label="alpha=0.9")
# plt.savefig("search.jpg")
plt.title('Superior Performance')
plt.xlabel('Time')
plt.ylabel('Performance')
plt.legend()
# plt.show()
plt.savefig("Superior_Performance.jpg")

t1 = time.time()
print("Time spent: ", t1-t0)