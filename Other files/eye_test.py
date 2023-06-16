import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Load eye tracking data
with open('raw_data.json', 'r') as f:
    data = json.load(f)

# Prepare data for the path plot
x_vals = []
y_vals = []
for key, value in data.items():
    # If greater then 50 iters, break
    if int(key) > 50000:
        break
    x_vals.append(value['xprediction'])
    y_vals.append(value['yprediction'])

# Create the plot
fig, ax = plt.subplots()

# Initialize the line and scatter objects
line, = ax.plot([], [], color='blue')
scatter = ax.scatter([], [], c='red', alpha=0.5)

def init():
    ax.set_xlim(min(x_vals), max(x_vals))
    ax.set_ylim(min(y_vals), max(y_vals))
    return line, scatter

def update(frame):
    line.set_data(x_vals[:frame+1], y_vals[:frame+1])
    scatter.set_offsets(list(zip(x_vals[:frame+1], y_vals[:frame+1])))
    return line, scatter

ani = animation.FuncAnimation(fig, update, frames=len(x_vals), init_func=init, blit=True)

plt.title('2D Animated Gaze Path of Eye Tracking Data')
ax.set_xlabel('X Prediction')
ax.set_ylabel('Y Prediction')
plt.savefig("figure3.png")
ani.save("animation.gif", writer='pillow')

plt.show()
