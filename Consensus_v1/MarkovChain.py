# -*- coding: utf-8 -*-
# @Time     : 7/11/2022 19:08
# @Author   : Junyi
# @FileName: MarkovChain.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np

# Markov Chain
class MarkovChain:
    def __init__(self, transition_matrix=None, state_list=None, initial_state=None):
        self.transition_matrix = transition_matrix
        self.state_list = state_list
        self.initial_state = initial_state
        self.index_dict = {self.state_list[index]: index for index in range(len(self.state_list))}
        self.state_dict = {index: self.state_list[index] for index in range(len(self.state_list))}

    def next_state(self):
        pass


if __name__ == '__main__':
    # Transition_matrix = np.array([[0.2, 0.1, 0.1, 0.1, 0.1],
    #                                           [0.2, 0.1, 0.15, 0.1, 0.1],
    #                                           [0.2, 0.1, 0.25, 0.1, 0.1],
    #                                           [0.2, 0.5, 0.25, 0.6, 0.4],
    #                                           [0.2, 0.2, 0.25, 0.1, 0.3]])
    Transition_matrix = np.array([[0.15, 0.25, 0.25, 0.25, 0.2],
                                              [0.25, 0.15, 0.25, 0.25, 0.2],
                                              [0.25, 0.25, 0.15, 0.25, 0.2],
                                              [0.25, 0.25, 0.25, 0.15, 0.2],
                                              [0.1, 0.1, 0.1, 0.1, 0.2]])
    # Transition_matrix = np.array([[0.2, 0.2, 0.2], [0.5, 0.5, 0.5], [0.3, 0.3, 0.3]])
    print("Transition_matrix", Transition_matrix)
    # state_distribution1 = np.array([0.8, 0.05, 0.05, 0.05, 0.05])  # [0.11111111 0.11764706 0.13071895 0.4624183  0.17810458]
    state_distribution1 = np.array([0.5, 0.1, 0.1, 0.1, 0.2])

    # state_distribution2 = np.array([0.3, 0.6, 0.1])
    # state_distribution3 = np.array([0.5, 0.2, 0.3])
    state_distribution_next = state_distribution1
    n = 100  # 可以调整推演的天数
    for i in range(n):
        state_distribution_next = np.dot(Transition_matrix, state_distribution_next)
        print("状态1", "第n次", i + 1, "的状态概率分布", state_distribution_next)
    # state_distribution_next = state_distribution2
    # for i in range(n):
    #     state_distribution_next = np.dot(Transition_matrix, state_distribution_next)
    #     print("状态2", "第n次", i + 1, "的状态概率分布", state_distribution_next)
    # state_distribution_next = state_distribution3
    # for i in range(n):
    #     state_distribution_next = np.dot(Transition_matrix, state_distribution_next)
    #     print("状态3", "第n次", i + 1, "的状态概率分布", state_distribution_next)
    # test = [0.6, 0.65, 0.75, 1.95, 1.05]
    test = [sum(i) for i in Transition_matrix]
    test = [i / sum(test) for i in test]
    print("test", test)