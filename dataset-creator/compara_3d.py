import numpy as np
import json
import matplotlib.pyplot as plt
with open('p001g01_3d_gray.json') as f:
    gray = json.load(f)

with open('p001g01_3d_rgb.json') as f:
    rgb = json.load(f)

def get_3d_data(data):
    points_list = []
    loc = data['localizations']
    for dicio in loc:

        for obj in dicio['objects']:
        
            for joint in obj['keypoints']:
                points_list.append(joint['position']['x'])
                points_list.append(joint['position']['y'])
                points_list.append(joint['position']['z'])
        
    return np.array(points_list)

gray = get_3d_data(gray)
rgb = get_3d_data(rgb)
print(gray.shape)
print(rgb.shape)

dif = (np.abs(gray - rgb))

plt.plot(dif)