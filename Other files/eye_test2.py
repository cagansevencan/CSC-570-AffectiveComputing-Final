import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Load eye tracking data
with open('raw_data.json', 'r') as f:
    data = json.load(f)

# Prepare data for the path plot
x_vals = []
y_vals = []
for key, value in data.items():
    x_vals.append(value['xprediction'])
    y_vals.append(value['yprediction'])

df = pd.DataFrame({
    'X': x_vals,
    'Y': y_vals
})

# Create the plot
fig, ax = plt.subplots()

# Create a heatmap using numpy's histogram2d and matplotlib's imshow
heatmap, xedges, yedges = np.histogram2d(df['X'], df['Y'], bins=(64,64))
extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]

ax.imshow(heatmap.T, extent=extent, origin='lower', cmap='hot', alpha=0.5)

# Plot the gaze path
ax.plot(x_vals, y_vals, color='cyan')

# Plot scatter points
ax.scatter(x_vals, y_vals, c='white', s=10)

plt.title('2D Gaze Path and Heatmap of Eye Tracking Data')
ax.set_xlabel('X Prediction')
ax.set_ylabel('Y Prediction')
plt.savefig("figure4.png")
plt.show()

