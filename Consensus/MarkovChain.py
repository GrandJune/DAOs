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
    Transition_matrix = np.array([[0.2, 0.1, 0.5, 0.1, 0.1],
                                  [0.5, 0.7, 0.4, 0.1, 0.1],
                                  [0.28, 0.18, 0.06, 0.1, 0.1],
                                  [0.01, 0.01, 0.01, 0.6, 0.1],
                                  [0.01, 0.01, 0.01, 0.1, 0.6]])
    # Transition_matrix = np.array([[0.2, 0.2, 0.2], [0.5, 0.5, 0.5], [0.3, 0.3, 0.3]])
    print("Transition_matrix", Transition_matrix)
    state_distribution1 = np.array([0.2, 0.1, 0.1, 0.1, 0.5])  # [0.13374385 0.40631994 0.12285496 0.02235605 0.02235605]
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