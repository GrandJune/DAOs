# -*- coding: utf-8 -*-
# @Time     : 7/19/2022 19:05
# @Author   : Junyi
# @FileName: Superior.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np
import math
from Reality import Reality
from Manager import Manager


class Superior:
    def __init__(self, policy_num=None, manager_num=None,
                 reality=None, p1=None, p2=None, initialization=1):
        """
        March's model to model how the traditional organizational cognition is formed.
        :param m: problem dimension (the length of policy directives, i.e., m // s)
        :param n: group size, 50 in March's model
        :param reality: policy reality
        :param p1: belief learning from code
        :param p2: code learning from belief
        """
        self.policy_num = policy_num  # policy length
        self.manager_num = manager_num  # the number of subunits under this superior
        self.p1 = p1  # agent learning from code, 0.1
        self.p2 = p2  # code learning from belief, 0.9
        self.reality = reality
        self.managers = []
        for _ in range(self.manager_num):
            manager = Manager(policy_num=self.policy_num, reality=self.reality, p1=self.p1, initialization=initialization)
            self.managers.append(manager)
        self.code = [0] * self.policy_num  # the initialization of code is zero
        self.code_payoff = 0
        self.superior_group = []
        self.performance_average_across_time = []

    def search(self):
        self.get_superior_group()
        self.learn_from_superior_group()  # using p2
        for manager in self.managers:
            manager.learn_from_code(code=self.code)  # using p1
        performance_list = [manager.payoff for manager in self.managers]
        self.performance_average_across_time.append(sum(performance_list) / len(performance_list))

    def get_majority_view(self, superior_policy_list=None):
        majority_view = [0] * self.policy_num
        for i in range(self.policy_num):
            temp = [policy[i] for policy in superior_policy_list]
            if sum(temp) > 0:
                majority_view[i] = 1
            elif sum(temp) < 0:
                majority_view[i] = -1
        return majority_view

    def get_superior_group(self):
        self.superior_group = []
        for manager in self.managers:
            if manager.payoff > self.code_payoff:
                self.superior_group.append(manager)

    def learn_from_superior_group(self):
        if self.superior_group:
            policy_list = [manager.policy for manager in self.superior_group]
            dominant_policy = self.get_majority_view(superior_policy_list=policy_list)
            # print("dominant_policy: ", dominant_policy)
            for index in range(self.policy_num):
                if self.code[index] == dominant_policy[index]:
                    continue
                else:
                    # those whose belief differ from the code, within superior group
                    differ_count = 0  # k in March's paper, pg.74, footnote
                    for manager in self.superior_group:
                        if manager.policy[index] != self.code[index]:
                            differ_count += 1
                    # print("change Prob. :", 1 - (1 - self.p2) ** differ_count)
                    if np.random.uniform(0, 1) < 1 - (1 - self.p2) ** differ_count:
                        self.code[index] = dominant_policy[index]
        else:
            pass  # if there is no superior group, the code remain unchanged.
        self.code_payoff = self.reality.get_policy_payoff(policy=self.code)

    def turnover(self, turnover_rate=None):
        if turnover_rate:
            for manager in self.managers:
                manager.turnover(turnover_rate=turnover_rate)


if __name__ == '__main__':
    # m = 30
    # n = 50
    # p1 = 0.1  # belief learning from code
    # p2 = 0.9  # code learning from belief
    # p1_list = np.arange(0.1, 1.0, 0.1)
    # reality = Reality(m=m)
    # performance_list = []
    # for p1 in p1_list:
    #     superior = Superior(m=m, n=n, reality=reality, p1=p1, p2=p2)
    #     for index in range(100):
    #         superior.search()
    #     performance_list.append(superior.performance_average_across_time[-1])
    #     print("p1: ", p1)
    # import matplotlib.pyplot as plt
    # x = p1_list
    # plt.plot(x, performance_list, "k-", label="Superior")
    # plt.xlabel('P1', fontweight='bold', fontsize=10)
    # plt.ylabel('Performance', fontweight='bold', fontsize=10)
    # plt.legend(frameon=False, ncol=3, fontsize=10)
    # plt.show()


    # Single P1
    m = 90
    policy_num = m // 3
    manager_num = 50
    p1 = 0.1  # belief learning from code
    p2 = 0.1  # code learning from belief
    performance_list_across_repeat = []
    code_performance_list_across_repeat = []
    reality = Reality(m=m)
    superior = Superior(policy_num=policy_num, manager_num=manager_num, reality=reality, p1=p1, p2=p2)
    code_payoff_across_time = []
    for index in range(100):
        print(index, superior.code, superior.code_payoff)
        superior.search()
        # print(index)
        # code_payoff_across_time.append(superior.code_payoff)
    # code_performance_list_across_repeat.append(code_payoff_across_time)
    # performance_list_across_repeat.append(superior.performance_average_across_time)
    # results, results_2 = [], []
    # for period in range(repetition):
    #     temp = [performance_list[period] for performance_list in performance_list_across_repeat]
    #     results.append(sum(temp) / len(temp))
    #     temp_2 = [payoff_list[period] for payoff_list in code_performance_list_across_repeat]
    #     results_2.append(sum(temp_2) / len(temp_2))
    import matplotlib.pyplot as plt
    x = range(100)
    plt.plot(x, superior.performance_average_across_time, "k-", label="Average")
    # plt.plot(x, results_2, "k--", label="Code")
    plt.xlabel('Time', fontweight='bold', fontsize=10)
    plt.ylabel('Performance', fontweight='bold', fontsize=10)
    plt.legend(frameon=False, ncol=3, fontsize=10)
    plt.savefig("March.png", transparent=False, dpi=200)
    plt.show()