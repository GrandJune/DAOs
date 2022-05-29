# -*- coding: utf-8 -*-
# @Time     : 12/14/2021 20:16
# @Author   : Junyi
# @FileName: Simulator.py
# @Software  : PyCharm
# Observing PEP 8 coding style
from Landscape import Landscape
from Socialized_Agent import Agent
import numpy as np


class Simulator:

    def __init__(self, N=10, state_num=4, agent_num=500, search_iteration=100, IM_type=None,
                 K=0, k=0, gs_proportion=0.5, knowledge_num=20,
                 exposure_type="Self-interested", openness=None, frequency=None,
                 quality=1.0, S_exposed_to_S=None, G_exposed_to_G=None):
        self.N = N
        self.state_num = state_num
        # Landscape
        self.landscapes = None
        self.IM_type = IM_type
        self.K = K
        self.k = k
        # Agent crowd
        self.agents = []  # will be stable; only the initial state and search will change
        self.agent_num = agent_num
        self.knowledge_num = knowledge_num
        # Cognitive Search
        self.search_iteration = search_iteration

    def set_landscape(self):
        self.landscape = Landscape(N=self.N, state_num=self.state_num)
        self.landscape.type(IM_type=self.IM_type, K=self.K, k=self.k)
        self.landscape.initialize()

    def set_agent(self):
        for _ in range(self.agent_num):
            agent = Agent(N=self.N, landscape=self.landscape, state_num=self.state_num)
            agent.type(name="Specialist")
            self.agents.append(agent)

    def process(self, socialization_freq=1, footprint=False):
        self.set_landscape()
        self.set_agent()
        agent0 = self.agents[0]


if __name__ == '__main__':
    # Test Example
    N = 6
    state_num = 4
    K = 2
    k = 0
    IM_type = "Traditional Directed"
    openness = 0.5
    quality = 0.5
    agent_num = 500
    search_iteration = 50
    knowledge_num = 12
    # exposure_type = "Random"
    simulator = Simulator(N=N, state_num=state_num, agent_num=agent_num, search_iteration=search_iteration, IM_type=IM_type,
                 K=K, k=k, gs_proportion=0.5, knowledge_num=knowledge_num, openness=openness, quality=quality)
    simulator.process(socialization_freq=1, footprint=False)
    print("END")

