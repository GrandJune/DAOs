# -*- coding: utf-8 -*-
# @Time     : 4/19/2023 20:58
# @Author   : Junyi
# @FileName: Gini_calculator.py
# @Software  : PyCharm
# Observing PEP 8 coding style
import numpy as np

# Generate 1000 random numbers using the Pareto distribution
pareto_random_numbers = np.random.pareto(1, 10000)

# Define a function to calculate the Gini index
def gini_index(data):
    # Sort the data in ascending order
    sorted_data = np.sort(data)
    # Get the cumulative sum of the sorted data
    cumsum_data = np.cumsum(sorted_data)
    # Get the Lorenz curve
    Lorenz_curve = cumsum_data / np.sum(data)
    # Calculate the area under the Lorenz curve
    area_Lorenz_curve = np.trapz(y=Lorenz_curve, x=np.linspace(0, 1, len(Lorenz_curve)))
    # Calculate the Gini index
    gini_index = 1 - 2 * area_Lorenz_curve
    return gini_index

# Calculate the Gini index for the generated random numbers
gini_index_value = gini_index(pareto_random_numbers)

# Print the Gini index value
print("The Gini index value for the generated random numbers is:", gini_index_value)
