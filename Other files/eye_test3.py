import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Load eye tracking data
with open('raw_data.json', 'r') as f:
    data = json.load(f)

# Prepare data for the plot
x_vals = []
y_vals = []
time_vals = []

for key, value in data.items():
    x_vals.append(value['xprediction'])
    y_vals.append(value['yprediction'])
    time_vals.append(float(key))

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot a 3D scatter plot
sc = ax.scatter(x_vals, y_vals, time_vals, c=time_vals, cmap='viridis')

# Add a colorbar to indicate the time progression
plt.colorbar(sc)

ax.set_xlabel('X Prediction')
ax.set_ylabel('Y Prediction')
ax.set_zlabel('Time')
plt.title('3D Gaze Path Over Time')

plt.savefig("figure2.png")
plt.show()
