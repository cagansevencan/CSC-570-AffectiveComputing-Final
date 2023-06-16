import cv2
import json
import numpy as np
import matplotlib.pyplot as plt

# Load the gaze data
with open('raw_data.json', 'r') as f:
    data = json.load(f)

# Convert data to numpy array
gaze_data = np.array([(value['xprediction'], value['yprediction']) for key, value in data.items()])

# Set up the bounding boxes for the areas of interest
areas_of_interest = np.array([
    [100, 100, 200, 200],  # [x1, y1, x2, y2]
    [300, 300, 400, 400],
    [500, 500, 600, 600]
])

# Set up an empty image to draw the attention map on
image = np.zeros((1080, 1920))

# Calculate the attention points
for x, y in gaze_data:
    for x1, y1, x2, y2 in areas_of_interest:
        if x1 < x < x2 and y1 < y < y2:
            image[int(y), int(x)] += 1

# Plot the attention map
plt.imshow(image, cmap='hot', interpolation='nearest')
plt.title('Attention Map')
plt.colorbar()
plt.savefig("figure1.png")
plt.show()
