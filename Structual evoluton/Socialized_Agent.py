# -*- coding: utf-8 -*-
# @Time     : 12/14/2021 19:59
# @Author   : Junyi
# @FileName: Agent.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import random
import numpy as np
from Landscape import Landscape


class Agent:

    def __init__(self, N, landscape=None, state_num=4, domain_num=0):
        """
        The difference between original one and the socialized one:
        1. copied_state: enable the angens to polish the existing ideas/solutions
        2. state_pool: the existing solutions in the community
        3. state_pool_rank: the personal rank regarding the existing solutions
        :param landscape:
        :param state_num:
        :param gs_ratio:
        :param cope_state: the observed state according to different exposure mechanisms
        """
        self.landscape = landscape
        self.N = N
        self.name = "None"
        self.state_num = state_num
        self.state = np.random.choice([cur for cur in range(self.state_num)], self.N).tolist()
        self.state = [str(i) for i in self.state]  # ensure the format of state
        # store the cognitive state list during the search
        self.domain_num = domain_num
        self.knowledge_domain = []
        self.decision_space = []  # all manageable elements' index: ['02', '03', '11', '13', '30', '31']
        self.freedom_space = []  # the alternatives for next step random selection: ['02', '13', '31'] given the current state '310*******'
        if not self.landscape:
            raise ValueError("Agent need to be assigned a landscape")
        self.fitness = self.landscape.query_fitness(state=self.state)
        self.fitness_rank = 0
        if (self.N != landscape.N) or (self.state_num != landscape.state_num):
            raise ValueError("Agent-Landscape Mismatch: please check your N and state number.")

    def type(self, name=None, specialist_num=0, generalist_num=0, element_num=0, gs_ratio=0.5):
        """
        Allocate one certain type to the agent
        :param name: the agent role
        :param specialist_num: the
        :param gs_ratio: the ratio of knowledge between G and S
        :return: Updating the agent characters
        """
        self.name = name
        self.knowledge_domain = np.random.choice(self.N, self.domain_num, replace=False).tolist()
        self.default_elements_in_unknown_domain = [str(index) + str(value) for index, value in enumerate(self.state)
                                                   if index not in self.knowledge_domain]
        self.decision_space = [str(i) + "0" for i in self.knowledge_domain]
        self.decision_space += [str(i) + "1" for i in self.knowledge_domain]
        self.update_freedom_space()

    def update_freedom_space(self):
        state_occupation = [str(i) + j for i, j in enumerate(self.state)]
        self.freedom_space = [each for each in self.decision_space if each not in state_occupation]

    def randomly_select_one(self):
        """
        Randomly select one element in the freedom space
        Local search for Specialist domains
        :return: selected position and corresponding value for state list/string
        """
        if len(self.decision_space) == 0:
            raise ValueError("Haven't initialize the decision space; Need to run type() function first")
        next_step = random.choice(self.freedom_space)
        cur_i, cur_j = next_step[0], next_step[1]
        return int(cur_i), cur_j

    def cognitive_local_search(self):
        """
        The core of this model where we define a consistent cognitive search framework for G/S role
        The Generalist domain follows the average pooling search
        The Specialist domain follows the mindset search
        There is a final random mapping after cognitive convergence, to map a vague state into a definite state
        """
        updated_position, updated_value = self.randomly_select_one()
        next_state = self.state.copy()
        next_state[updated_position] = updated_value
        current_fitness = self.landscape.query_fitness(self.state)
        next_fitness = self.landscape.query_fitness(next_state)
        if next_fitness > current_fitness:
            self.state = next_state
            self.fitness = current_fitness
            self.update_freedom_space()  # whenever state change, freedom space need to be changed
        else:
            self.fitness = current_fitness

    def describe(self):
        print("*********Agent information********* ")
        print("Agent type: ", self.name)
        print("N: ", self.N)
        print("State number: ", self.state_num)
        print("Current state list: ", self.state)
        print("Current fitness: ", self.fitness)
        print("Knowledge/Manageable domain: ", self.knowledge_domain)
        print("Freedom space: ", self.freedom_space)
        print("Decision space: ", self.decision_space)
        print("Unknown knowledge as default: ", self.default_elements_in_unknown_domain)
        print("********************************")


if __name__ == '__main__':
    # Test Example
    landscape = Landscape(N=8, state_num=2)
    landscape.type(IM_type="Factor Directed", K=0, k=42)
    landscape.initialize()
    agent = Agent(N=8, landscape=landscape, state_num=2, domain_num=4)
    agent.type(name="T shape", generalist_num=1, specialist_num=7)
    agent.describe()
    for _ in range(100):
        agent.cognitive_local_search()
    agent.converged_fitness = agent.landscape.query_fitness(state=agent.state)
    agent.describe()
    print("END")



