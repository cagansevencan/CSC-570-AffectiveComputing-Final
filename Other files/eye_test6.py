import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from PIL import Image
import seaborn as sns

# Load the gaze data
with open('raw_data.json', 'r') as f:
    data = json.load(f)

# Convert data to numpy array and calculate dwell times
gaze_points = []
prev_time = None
prev_point = None
for time, value in sorted(data.items(), key=lambda x: float(x[0])):
    if(float(time) > 30000):
        break
    point = np.array([value['xprediction'], value['yprediction'], float(time)])
    gaze_points.append(point)
    prev_time = time
    prev_point = point

gaze_points = np.array(gaze_points)

# Load background image
img = Image.open('wallpaperflare.com_wallpaper.jpg')
background_image = np.array(img)

# Create figure and axes
fig, ax = plt.subplots()

def update(frame):
    ax.clear()
    ax.imshow(background_image, extent=[gaze_points[:, 0].min(), gaze_points[:, 0].max(), gaze_points[:, 1].min(), gaze_points[:, 1].max()])
    ax.set_xlim(gaze_points[:, 0].min(), gaze_points[:, 0].max())
    ax.set_ylim(gaze_points[:, 1].min(), gaze_points[:, 1].max())
    ax.set_title('Gaze points over time')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    # KDE plot
    sns.kdeplot(x=gaze_points[:frame, 0], y=gaze_points[:frame, 1], fill=False, thresh=0, levels=100, cmap="magma", alpha=0.25, ax=ax, common_norm=False)
    sc = ax.scatter(gaze_points[:frame, 0], gaze_points[:frame, 1], color='black', s=10)
    return sc,

# Skip every 10 frames to speed up the animation
ani = FuncAnimation(fig, update, frames=np.arange(0, len(gaze_points), 10), blit=False, interval=200)
# ani = FuncAnimation(fig, update, frames=len(gaze_points), blit=False, interval=200)
ani.save("animation3.gif", writer='pillow')
plt.show()
