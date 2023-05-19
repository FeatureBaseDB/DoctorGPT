import matplotlib.pyplot as plt
import numpy as np

start = 1
reset = start
angle = 0.1
inc = 300
length = 7
stroke_weight = 2

def collatz(n):
    if n % 2 == 0:
        return n / 2
    else:
        return (n * 3 + 1) / 2

fig, ax = plt.subplots()
ax.set_aspect('equal')
ax.axis('off')

while start <= 5000:
    sequence = []
    n = start
    while n != 1:
        sequence.append(n)
        n = collatz(n)
    sequence.append(1)
    sequence.reverse()

    x, y = 0, 0
    print(sequence)
    for j, value in enumerate(sequence):
        if j == 6:
            angle_rotation = 0  # Special case when j is 6
        else:
            angle_rotation = j / (j - 6) * angle

        dx = length * np.sin(angle_rotation)
        dy = -length * np.cos(angle_rotation)

        color = (j / len(sequence), 1, 0.2, 0.2)
        ax.plot([x, x + dx], [y, y + dy], color=color, linewidth=stroke_weight)

        x += dx
        y += dy

    start += inc
    if start > 5000:
        reset += 1
        start = reset

plt.show()
