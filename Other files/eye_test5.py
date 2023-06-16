import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.colors as mcolors

# Load the gaze data
with open('raw_data.json', 'r') as f:
    data = json.load(f)

# Convert data to numpy array and calculate dwell times
gaze_points = []
dwell_times = []
prev_time = None
prev_point = None
for time, value in sorted(data.items(), key=lambda x: float(x[0])):
    # Break if time is greater than 10 seconds
    if float(time) > 10000:
        break
    point = np.array([value['xprediction'], value['yprediction'], float(time)])
    if prev_point is not None:
        dwell_time = np.linalg.norm(point - prev_point)
        dwell_times.append(dwell_time)
    gaze_points.append(point)
    prev_time = time
    prev_point = point

gaze_points = np.array(gaze_points)
dwell_times = np.array(dwell_times)

# Normalize time data for coloring
times = gaze_points[:, 2]
times = (times - times.min()) / (times.max() - times.min())

# Create a colormap
cmap = plt.get_cmap('jet')

fig, ax = plt.subplots()

def update(frame):
    ax.clear()
    ax.set_xlim(gaze_points[:, 0].min(), gaze_points[:, 0].max())
    ax.set_ylim(gaze_points[:, 1].min(), gaze_points[:, 1].max())
    ax.set_title('Gaze points over time')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')

    for i in range(frame):
        alpha = 1 - (frame - i) / len(gaze_points)
        ax.scatter(gaze_points[i, 0], gaze_points[i, 1], c=cmap(times[i]), alpha=alpha, s=5)

    return None

ani = FuncAnimation(fig, update, frames=len(gaze_points), blit=False, interval=20)
ani.save("animation2.gif", writer='pillow')
plt.show()
