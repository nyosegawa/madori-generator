import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import sys

def draw_apartment(apartment_data):
    _, ax = plt.subplots()
    for room in apartment_data["apartment"]["rooms"]:
        room_rect = room["rectangle"]
        ax.add_patch(patches.Rectangle((room_rect["x"], room_rect["y"]), room_rect["width"], room_rect["height"], edgecolor='black', facecolor='none'))
        plt.text(room_rect["x"] + room_rect["width"]/2, room_rect["y"] + room_rect["height"]/2, room["name"],
                horizontalalignment='center', verticalalignment='center')

        for feature in room["features"]:
            feature_rect = feature["rectangle"]
            if feature["type"] == "window":
                color = 'blue'
            elif feature["type"] == "door":
                color = 'green'
            else:
                color = 'red'
            ax.add_patch(patches.Rectangle((feature_rect["x"], feature_rect["y"]), feature_rect["width"], feature_rect["height"], edgecolor=color, facecolor='none'))

    ax.set_xlim(0, apartment_data["apartment"]["rectangle"]["width"])
    ax.set_ylim(0, apartment_data["apartment"]["rectangle"]["height"])
    ax.set_aspect('equal')
    plt.gca().invert_yaxis()
    plt.show()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            apartment_data = json.load(f)
    else:
        with open('./sample.json') as f:
            apartment_data = json.load(f)
    draw_apartment(apartment_data)