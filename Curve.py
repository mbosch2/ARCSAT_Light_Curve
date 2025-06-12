import matplotlib.pyplot as plt
from datetime import datetime
"""
Once the photometry code is run, this code will use the created list to make a graph
"""
#We find the times and put them into a new list of just Hours Minutes Seconds
x_vals = [datetime.fromisoformat(ts) for ts in times]
time_labels = [ts.strftime('%H:%M:%S') for ts in x_vals]

#We normalize the flux 
#log_ap = numpy.log10(aperture_sums)
y_vals = aperture_sums/numpy.max(aperture_sums)

#We sort the lists together so that they are time ordered
combined = list(zip(time_labels, y_vals))
combined.sort(key=lambda x: x[0])

# Unzip the sorted pairs back into two lists
time_labels, y_vals = zip(*combined)

# Convert back to lists if needed
time_labels = list(time_labels)
y_vals = list(y_vals)

# Create the plot
plt.figure(figsize=(10, 5))
plt.scatter(time_labels, y_vals, s=10, marker='o')
plt.ylim(0.75, 1.05)
plt.xlabel('Time (UTC)')
plt.ylabel('Flux normalized to Maximum')
plt.gca().xaxis.set_major_locator(plt.MaxNLocator(5))
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('Light_curve_1')
