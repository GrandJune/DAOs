import matplotlib.pyplot as plt
import numpy as np

# Generate random data for the histogram
data = np.random.normal(100, 10, 1000)

# Plot the histogram using the default settings
plt.hist(data, bins=20, edgecolor='k')

# Add labels and formatting to the figure
plt.xlabel('Value')
plt.ylabel('Frequency')
plt.title('Histogram of Random Data')

# Save the figure to a file
plt.savefig('histogram.pdf', bbox_inches='tight')

# Show the figure
plt.show()
