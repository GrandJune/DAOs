# -*- coding: utf-8 -*-
# @Time     : 2/2/2024 20:54
# @Author   : Junyi
# @FileName: Autonomy_2_Isolation.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import networkx as nx
import random
import numpy as np
import multiprocessing as mp
import time
from multiprocessing import Semaphore
import pickle


def func(num_nodes=None, num_neighbors=None, autonomous_prob=None, loop=None, return_dict=None, sema=None):
    np.random.seed(None)
    nodes = range(num_nodes)
    node_performance = [np.random.uniform(low=0, high=1) for i in range(num_nodes)]
    G = nx.Graph()
    for node in nodes:
        # Randomly select 7 superior nodes (excluding the focal node)
        first_superior_nodes = [index for index, performance in zip(nodes, node_performance) if
                                performance >= node_performance[node]]
        first_superior_nodes.remove(node)
        if len(first_superior_nodes) > num_neighbors:
            first_suggested_nodes = random.sample(first_superior_nodes, num_neighbors)
        else:
            first_suggested_nodes = first_superior_nodes
        for neighbor in first_suggested_nodes:
            # Check if the neighbor also suggests the focal node
            second_superior_nodes = [index for index, performance in zip(nodes, node_performance) if
                                     performance >= node_performance[neighbor]]
            second_superior_nodes.remove(neighbor)
            if len(second_superior_nodes) > num_neighbors:
                second_suggested_nodes = random.sample(second_superior_nodes, num_neighbors)
                if node in second_suggested_nodes:
                    G.add_edge(node, neighbor)
                else:
                    if np.random.uniform(0, 1) >= autonomous_prob:  # Non-autonomy; Being forced
                        G.add_edge(node, neighbor)
            else:
                second_suggested_nodes = second_superior_nodes
                if node in second_suggested_nodes:
                    G.add_edge(node, neighbor)
                else:
                    if np.random.uniform(0, 1) >= autonomous_prob:  # Non-autonomy; Being forced
                        G.add_edge(node, neighbor)
    isolated_nodes = list(set(nodes) - set(G.nodes()))
    # Step 5: Calculate the average distance for each sub-network
    connected_components = list(nx.connected_components(G))
    average_distances = []
    for component in connected_components:
        subgraph = G.subgraph(component)
        if len(subgraph) > 1:
            average_distance = nx.average_shortest_path_length(subgraph)
            average_distances.append(average_distance)

    # Step 6: Calculate the overall average distance
    if average_distances:
        overall_average_distance = np.mean(average_distances)
        print(f"Overall average distance: {overall_average_distance}")
    else:
        overall_average_distance = 0
        print("The graph is disconnected.")
    num_subnetworks = nx.number_connected_components(G)
    num_isolations = num_subnetworks + len(isolated_nodes)
    return_dict[loop] = [num_isolations, num_subnetworks, len(isolated_nodes), overall_average_distance]
    sema.release()


if __name__ == '__main__':
    t0 = time.time()
    num_nodes = 1000
    num_neighbors = 7
    autonomous_prob_list = np.arange(0.02, 1.02, 0.02).tolist()
    concurrency = 100
    repetition = 100
    (num_isolation_across_autonomy, num_subnetwork_across_autonomy,
     num_isolated_node_across_autonomy, distance_across_autonomy) = [], [], [], []
    for autonomous_prob in autonomous_prob_list:
        sema = Semaphore(concurrency)
        manager = mp.Manager()
        jobs = []
        return_dict = manager.dict()
        for loop in range(repetition):
            sema.acquire()
            p = mp.Process(target=func, args=(num_nodes, num_neighbors, autonomous_prob, loop, return_dict, sema))
            jobs.append(p)
            p.start()
        for proc in jobs:
            proc.join()
        results = return_dict.values()  # Don't need dict index, since it is repetition.
        # emerge the hyper_loop
        num_isolation_across_autonomy.append(sum([result[0] for result in results]) / repetition)
        num_subnetwork_across_autonomy.append(sum([result[1] for result in results]) / repetition)
        num_isolated_node_across_autonomy.append(sum([result[2] for result in results]) / repetition)
        distance_across_autonomy.append(sum([result[3] for result in results]) / repetition)
    with open("num_isolated_node_across_autonomy_2", 'wb') as out_file:
        pickle.dump(num_isolation_across_autonomy, out_file)
    with open("num_subnetwork_across_autonomy_2", 'wb') as out_file:
        pickle.dump(num_subnetwork_across_autonomy, out_file)
    with open("num_isolated_node_across_autonomy_2", 'wb') as out_file:
        pickle.dump(num_isolated_node_across_autonomy, out_file)
    with open("distance_across_autonomy", 'wb') as out_file:
        pickle.dump(distance_across_autonomy, out_file)

    t1 = time.time()
    print(time.strftime("%H:%M:%S", time.gmtime(t1-t0)))